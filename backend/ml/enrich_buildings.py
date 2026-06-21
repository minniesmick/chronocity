"""
ML-1: Building data enrichment pipeline.

Usage:
  python enrich_buildings.py --city new-york --source pluto
  python enrich_buildings.py --city berlin   --source geoportal
  python enrich_buildings.py --city all      --source ghsl

Output: enriched GeoJSON written back to public/cities/{city}/buildings.geojson
with added fields: construction_year (if missing), data_source
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent  # chronocity/
PUBLIC = ROOT / "public" / "cities"

# ── helpers ───────────────────────────────────────────────────────────────────

def load_geojson(city: str) -> dict:
    path = PUBLIC / city / "buildings.geojson"
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save_geojson(city: str, data: dict) -> None:
    path = PUBLIC / city / "buildings.geojson"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  Saved → {path}")

def stats(data: dict, label: str) -> None:
    features = data["features"]
    total = len(features)
    has_year = sum(1 for f in features if f["properties"].get("construction_year"))
    sources = {}
    for f in features:
        s = f["properties"].get("data_source", "OSM")
        sources[s] = sources.get(s, 0) + 1
    print(f"\n[{label}] total={total}  year_filled={has_year} ({has_year*100//total}%)")
    for src, cnt in sorted(sources.items()):
        print(f"  {src}: {cnt}")

# ── NYC PLUTO ─────────────────────────────────────────────────────────────────

def enrich_nyc_pluto(raw_path: Path | None = None) -> None:
    """
    Spatial join NYC buildings.geojson with PLUTO MapPLUTO shapefile.

    PLUTO download (free, ~300MB):
      https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks
      → Export → Shapefile → save to backend/ml/data/raw/pluto/

    Key field: YearBuilt (int)
    """
    import geopandas as gpd
    from shapely.geometry import shape

    print("\n=== NYC PLUTO enrichment ===")

    # Load OSM buildings
    osm = load_geojson("new-york")
    osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
    print(f"  OSM buildings: {len(osm_gdf)}")

    # Load PLUTO
    if raw_path is None:
        raw_path = Path(__file__).parent / "data" / "raw" / "pluto"
    shp_files = list(raw_path.glob("*.shp"))
    if not shp_files:
        print(f"  ERROR: No .shp file found in {raw_path}")
        print("  Download MapPLUTO from:")
        print("    https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks")
        print("  → Export → Shapefile → extract to backend/ml/data/raw/pluto/")
        return

    pluto = gpd.read_file(shp_files[0]).to_crs("EPSG:4326")
    print(f"  PLUTO lots: {len(pluto)}")

    # Keep only YearBuilt column, drop empty
    pluto = pluto[["geometry", "YearBuilt"]].dropna(subset=["YearBuilt"])
    pluto = pluto[pluto["YearBuilt"] > 1800]
    pluto["YearBuilt"] = pluto["YearBuilt"].astype(int)

    # Spatial join: each OSM building centroid → nearest PLUTO lot
    osm_gdf["centroid"] = osm_gdf.geometry.centroid
    osm_cents = osm_gdf.copy()
    osm_cents.geometry = osm_cents["centroid"]

    joined = gpd.sjoin_nearest(osm_cents, pluto, how="left", max_distance=0.001)
    print(f"  Matched: {joined['YearBuilt'].notna().sum()} / {len(joined)}")

    # Write back to GeoJSON
    updated = 0
    for i, feat in enumerate(osm["features"]):
        props = feat["properties"]
        year = joined.iloc[i]["YearBuilt"] if i < len(joined) else None
        if year and (not props.get("construction_year")):
            props["construction_year"] = int(year)
            props["data_source"] = "NYC_PLUTO"
            updated += 1
        elif props.get("construction_year"):
            props.setdefault("data_source", "NYC_PLUTO")

    print(f"  Updated {updated} buildings with PLUTO year")
    stats(osm, "new-york after PLUTO")
    save_geojson("new-york", osm)

# ── Berlin Geoportal ──────────────────────────────────────────────────────────

def enrich_berlin_geoportal(raw_path: Path | None = None) -> None:
    """
    Spatial join Berlin buildings.geojson with Berlin Geoportal Baujahr data.

    Berlin Geoportal (free WFS/Shapefile):
      https://www.stadtentwicklung.berlin.de/geoinformation/fis-broker/
      Layer: "Blockkarte 1:5000 (ISU5)" or "Gebäude mit Baujahr" (LOD1/LOD2)
      → Download as GeoJSON/Shapefile → save to backend/ml/data/raw/berlin_geoportal/

    Alternative direct download:
      https://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_gebaeude/
    """
    import geopandas as gpd

    print("\n=== Berlin Geoportal enrichment ===")

    osm = load_geojson("berlin")
    osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
    print(f"  OSM buildings: {len(osm_gdf)}")

    if raw_path is None:
        raw_path = Path(__file__).parent / "data" / "raw" / "berlin_geoportal"

    files = list(raw_path.glob("*.geojson")) + list(raw_path.glob("*.shp"))
    if not files:
        print(f"  ERROR: No file found in {raw_path}")
        print("  Download Berlin building data (with Baujahr/year_built field) from:")
        print("    https://www.stadtentwicklung.berlin.de/geoinformation/fis-broker/")
        print("  → save to backend/ml/data/raw/berlin_geoportal/")
        return

    src = gpd.read_file(files[0]).to_crs("EPSG:4326")
    print(f"  Geoportal features: {len(src)}")

    # Find year column (Baujahr, year_built, bj, etc.)
    year_col = next((c for c in src.columns if "bau" in c.lower() or "year" in c.lower() or c.lower() in ("bj", "baujahr")), None)
    if not year_col:
        print(f"  ERROR: Could not find year column. Columns: {list(src.columns)}")
        return
    print(f"  Using column: '{year_col}'")

    src = src[["geometry", year_col]].dropna(subset=[year_col])
    src = src[src[year_col].astype(float) > 1800]
    src[year_col] = src[year_col].astype(float).astype(int)

    osm_gdf["centroid"] = osm_gdf.geometry.centroid
    osm_cents = osm_gdf.copy()
    osm_cents.geometry = osm_cents["centroid"]

    joined = gpd.sjoin_nearest(osm_cents, src, how="left", max_distance=0.0005)

    updated = 0
    for i, feat in enumerate(osm["features"]):
        props = feat["properties"]
        year = joined.iloc[i][year_col] if i < len(joined) else None
        if year and not props.get("construction_year"):
            props["construction_year"] = int(year)
            props["data_source"] = "Berlin_Geoportal"
            updated += 1
        elif props.get("construction_year"):
            props.setdefault("data_source", "OSM")

    print(f"  Updated {updated} buildings")
    stats(osm, "berlin after Geoportal")
    save_geojson("berlin", osm)

# ── GHSL (all cities) ─────────────────────────────────────────────────────────

def enrich_ghsl(cities: list[str], raw_path: Path | None = None) -> None:
    """
    Enrich buildings using GHSL (Global Human Settlement Layer) built-up year raster.

    GHSL BUILT_S dataset (free, EU JRC):
      https://human-settlement.emergency.copernicus.eu/download.php
      Layer: GHS_BUILT_S_ANBH_E2030_GLOBE_R2023A_54009_100_V1_0
      OR epoch-specific: GHS_BUILT_S_E1975_GLOBE_R2023A (one per decade)

    Simpler: GHS-BUILT-C (built-up characteristics) includes construction epoch.
      Download GeoTIFF for Europe/Asia/Americas as needed.
      → save to backend/ml/data/raw/ghsl/

    Note: GHSL is a raster. We sample the raster value at each building centroid.
    Epoch values: 1 = before 1975, 2 = 1975-1990, 3 = 1990-2000, 4 = 2000-2014, 5 = 2014+
    """
    try:
        import rasterio
        from rasterio.sample import sample_gen
        import numpy as np
    except ImportError:
        print("  ERROR: rasterio not installed. Run: pip install rasterio")
        return

    if raw_path is None:
        raw_path = Path(__file__).parent / "data" / "raw" / "ghsl"

    tif_files = list(raw_path.glob("*.tif")) + list(raw_path.glob("*.tiff"))
    if not tif_files:
        print(f"\nERROR: No GHSL .tif found in {raw_path}")
        print("  Download from: https://human-settlement.emergency.copernicus.eu/download.php")
        print("  Layer: GHS_BUILT_C_MSZ_E2018_GLOBE_R2023A_54009_10_V1_0")
        return

    # GHSL epoch → approximate year
    EPOCH_TO_YEAR = {1: 1950, 2: 1982, 3: 1995, 4: 2007, 5: 2018}

    for city in cities:
        print(f"\n=== GHSL enrichment: {city} ===")
        osm = load_geojson(city)
        import geopandas as gpd
        gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
        centroids = [(geom.centroid.x, geom.centroid.y) for geom in gdf.geometry]

        updated = 0
        with rasterio.open(tif_files[0]) as src:
            from pyproj import Transformer
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            proj_coords = [transformer.transform(lon, lat) for lon, lat in centroids]
            values = list(sample_gen(src, proj_coords))

        for i, (feat, val) in enumerate(zip(osm["features"], values)):
            props = feat["properties"]
            if props.get("construction_year"):
                props.setdefault("data_source", "OSM")
                continue
            epoch = int(val[0]) if val[0] and val[0] > 0 else None
            if epoch and epoch in EPOCH_TO_YEAR:
                props["construction_year"] = EPOCH_TO_YEAR[epoch]
                props["data_source"] = "GHSL"
                updated += 1

        print(f"  Updated {updated} buildings")
        stats(osm, f"{city} after GHSL")
        save_geojson(city, osm)

# ── Mark remaining as OSM ─────────────────────────────────────────────────────

def mark_osm_source(city: str) -> None:
    """Add data_source: 'OSM' to all features that don't have one yet."""
    osm = load_geojson(city)
    for feat in osm["features"]:
        feat["properties"].setdefault("data_source", "OSM")
    save_geojson(city, osm)
    print(f"  {city}: OSM source tag applied")

# ── CLI ───────────────────────────────────────────────────────────────────────

ALL_CITIES = ["new-york", "berlin", "paris", "vienna", "chicago", "london", "tokyo", "istanbul", "barcelona", "madrid", "moscow"]

def main():
    parser = argparse.ArgumentParser(description="ChronoCity building data enrichment")
    parser.add_argument("--city",   default="new-york", help="City id or 'all'")
    parser.add_argument("--source", choices=["pluto", "geoportal", "ghsl", "mark-osm", "all"], default="pluto")
    parser.add_argument("--raw",    help="Override raw data directory path")
    args = parser.parse_args()

    cities = ALL_CITIES if args.city == "all" else [args.city]
    raw = Path(args.raw) if args.raw else None

    if args.source in ("pluto", "all") and "new-york" in cities:
        enrich_nyc_pluto(raw)

    if args.source in ("geoportal", "all") and "berlin" in cities:
        enrich_berlin_geoportal(raw)

    if args.source in ("ghsl", "all"):
        ghsl_cities = [c for c in cities if c not in ("new-york", "berlin")] if args.source == "all" else cities
        enrich_ghsl(ghsl_cities, raw)

    if args.source == "mark-osm":
        for city in cities:
            mark_osm_source(city)

if __name__ == "__main__":
    main()
