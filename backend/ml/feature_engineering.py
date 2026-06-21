"""
ML-2: Feature engineering for building era prediction.

Outputs:
  D:/PROJELER/ml_data/features_all.parquet   — all 11 cities, all features
  D:/PROJELER/ml_data/train.parquet          — labeled buildings (train cities)
  D:/PROJELER/ml_data/test_gt.parquet        — labeled buildings (test cities, ground truth)
  D:/PROJELER/ml_data/predict.parquet        — unlabeled buildings (all cities, for inference)

Era classes (7):
  0 = Tas_Barok   (<1870)
  1 = Grunderzeit (1870-1918)
  2 = Art_Deco    (1918-1945)
  3 = Brutalizm   (1945-1965)
  4 = Prefab      (1965-1980)
  5 = Cam_Celik   (1980-2000)
  6 = Modern      (>=2000)
"""

import json, math
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
from pyproj import Transformer
from sklearn.neighbors import BallTree

ROOT = Path(__file__).parent.parent.parent
PUBLIC = ROOT / "public" / "cities"
OUT = Path(r"D:\PROJELER\ml_data")
OUT.mkdir(parents=True, exist_ok=True)

ALL_CITIES = [
    "new-york", "paris", "vienna", "chicago", "berlin", "moscow",
    "london", "barcelona", "madrid", "tokyo", "istanbul",
]

TRAIN_CITIES = {"new-york", "paris", "vienna", "chicago", "berlin", "moscow"}
TEST_CITIES  = {"london", "barcelona", "madrid", "tokyo", "istanbul"}

CITY_CENTERS = {
    "new-york":  (-73.988,  40.748),
    "paris":     (2.352,    48.856),
    "vienna":    (16.373,   48.208),
    "chicago":   (-87.628,  41.878),
    "berlin":    (13.405,   52.520),
    "moscow":    (37.617,   55.755),
    "london":    (-0.080,   51.505),
    "barcelona": (2.164,    41.389),
    "madrid":    (-3.695,   40.416),
    "tokyo":     (139.745,  35.690),
    "istanbul":  (28.965,   41.013),
}

ERA_BOUNDARIES = [1870, 1918, 1945, 1965, 1980, 2000]
ERA_NAMES = ["Tas_Barok", "Grunderzeit", "Art_Deco", "Brutalizm", "Prefab", "Cam_Celik", "Modern"]

def year_to_era(year):
    for i, boundary in enumerate(ERA_BOUNDARIES):
        if year < boundary:
            return i
    return len(ERA_BOUNDARIES)

def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def extract_geom_features(geom, transformer):
    """Extract geometric features from a polygon in WGS84."""
    try:
        proj = transformer.transform_geometry(geom)
        area = proj.area
        perim = proj.length
        compactness = (4 * math.pi * area / (perim ** 2)) if perim > 0 else 0
        bounds = proj.bounds  # minx, miny, maxx, maxy
        w = bounds[2] - bounds[0]
        h = bounds[3] - bounds[1]
        aspect = (max(w, h) / min(w, h)) if min(w, h) > 0 else 1.0
        coords = list(geom.exterior.coords) if hasattr(geom, 'exterior') else []
        n_verts = len(coords) - 1  # last coord == first
        return area, perim, compactness, aspect, n_verts
    except Exception:
        return 0.0, 0.0, 0.0, 1.0, 4

print("Loading buildings from all cities...")
records = []

for city in ALL_CITIES:
    path = PUBLIC / city / "buildings.geojson"
    if not path.exists():
        print(f"  MISSING: {city}")
        continue

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    cx, cy = CITY_CENTERS[city]
    # Use UTM-like local metric projection centered on city
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)

    features = data["features"]
    print(f"  {city}: {len(features)} buildings...", end=" ")

    for feat in features:
        props = feat.get("properties", {})
        geom_raw = feat.get("geometry")
        if not geom_raw:
            continue
        try:
            geom = shape(geom_raw)
            centroid = geom.centroid
            lon, lat = centroid.x, centroid.y
        except Exception:
            continue

        area, perim, compactness, aspect, n_verts = extract_geom_features(geom, transformer)
        height = props.get("height") or 0.0
        try:
            height = float(height)
        except Exception:
            height = 0.0

        construction_year = props.get("construction_year")
        ghsl_year = props.get("ghsl_neighborhood_year")
        data_source = props.get("data_source", "OSM")
        dist_center = haversine_km(lon, lat, cx, cy)

        era = year_to_era(int(construction_year)) if construction_year else None

        records.append({
            "city": city,
            "lon": lon,
            "lat": lat,
            "area_m2": area,
            "perimeter_m": perim,
            "compactness": compactness,
            "aspect_ratio": aspect,
            "n_vertices": n_verts,
            "height": height,
            "dist_to_center_km": dist_center,
            "ghsl_neighborhood_year": ghsl_year,
            "construction_year": construction_year,
            "data_source": data_source,
            "era": era,
        })

    labeled = sum(1 for r in records if r["city"] == city and r["era"] is not None)
    print(f"{labeled} labeled")

df = pd.DataFrame(records)
print(f"\nTotal: {len(df)} buildings, {df['era'].notna().sum()} labeled")

# ── Neighborhood features ──────────────────────────────────────────────────────
print("\nComputing neighborhood features (per city)...")

df["neighbor_mean_height"] = 0.0
df["neighbor_mean_year"] = np.nan
df["neighbor_std_year"] = np.nan
df["building_density_200m"] = 0

K = 50
DENSITY_RADIUS_KM = 0.2  # 200m

for city in ALL_CITIES:
    mask = df["city"] == city
    city_df = df[mask].copy()
    if len(city_df) < 2:
        continue

    coords_rad = np.radians(city_df[["lat", "lon"]].values)
    tree = BallTree(coords_rad, metric="haversine")

    # K nearest neighbors
    dist_k, idx_k = tree.query(coords_rad, k=min(K+1, len(city_df)))

    # Buildings within 200m
    radius_rad = DENSITY_RADIUS_KM / 6371.0
    idx_200m = tree.query_radius(coords_rad, r=radius_rad)

    heights = city_df["height"].values
    years = city_df["construction_year"].values

    mean_heights, mean_years, std_years, densities = [], [], [], []

    for i in range(len(city_df)):
        neighbors = idx_k[i][1:]  # exclude self
        mean_heights.append(float(np.mean(heights[neighbors])) if len(neighbors) > 0 else 0.0)

        neighbor_years = [years[j] for j in neighbors if years[j] is not None]
        if neighbor_years:
            yrs = [float(y) for y in neighbor_years]
            mean_years.append(float(np.mean(yrs)))
            std_years.append(float(np.std(yrs)))
        else:
            mean_years.append(np.nan)
            std_years.append(np.nan)

        densities.append(len(idx_200m[i]) - 1)  # exclude self

    df.loc[mask, "neighbor_mean_height"] = mean_heights
    df.loc[mask, "neighbor_mean_year"] = mean_years
    df.loc[mask, "neighbor_std_year"] = std_years
    df.loc[mask, "building_density_200m"] = densities
    print(f"  {city}: neighborhood features done")

# ── Fill NaN neighbor_year with city median ────────────────────────────────────
for city in ALL_CITIES:
    mask = df["city"] == city
    city_median = df.loc[mask & df["neighbor_mean_year"].notna(), "neighbor_mean_year"].median()
    if pd.notna(city_median):
        df.loc[mask & df["neighbor_mean_year"].isna(), "neighbor_mean_year"] = city_median
        df.loc[mask & df["neighbor_std_year"].isna(), "neighbor_std_year"] = 0.0
    if pd.notna(df.loc[mask, "ghsl_neighborhood_year"].median()):
        df.loc[mask & df["ghsl_neighborhood_year"].isna(), "ghsl_neighborhood_year"] = \
            df.loc[mask, "ghsl_neighborhood_year"].median()

# ── Save ───────────────────────────────────────────────────────────────────────
df.to_parquet(OUT / "features_all.parquet", index=False)
print(f"\nSaved features_all.parquet: {len(df)} rows")

FEATURE_COLS = [
    "area_m2", "perimeter_m", "compactness", "aspect_ratio", "n_vertices",
    "height", "dist_to_center_km", "ghsl_neighborhood_year",
    "neighbor_mean_height", "neighbor_mean_year", "neighbor_std_year",
    "building_density_200m", "lat", "lon",
]

labeled = df[df["era"].notna()].copy()
train_df  = labeled[labeled["city"].isin(TRAIN_CITIES)]
test_gt   = labeled[labeled["city"].isin(TEST_CITIES)]
predict   = df[df["era"].isna()].copy()

train_df.to_parquet(OUT / "train.parquet", index=False)
test_gt.to_parquet(OUT / "test_gt.parquet", index=False)
predict.to_parquet(OUT / "predict.parquet", index=False)

print(f"train.parquet:    {len(train_df)} rows ({train_df['city'].value_counts().to_dict()})")
print(f"test_gt.parquet:  {len(test_gt)} rows ({test_gt['city'].value_counts().to_dict()})")
print(f"predict.parquet:  {len(predict)} rows")
print(f"\nFeature columns: {FEATURE_COLS}")
print(f"\nEra distribution (train):\n{train_df['era'].value_counts().sort_index()}")
