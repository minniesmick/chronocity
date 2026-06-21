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
    Enrich buildings with construction_year using GHSL GHS_BUILT_S multi-epoch rasters.

    Strategy: sample 5 epoch rasters per building centroid, find FIRST epoch with
    non-zero built-up area → that epoch = approximate first_built year.

    Epochs: E1975 (pre-1975), E1990 (1975-90), E2000 (1990-2000),
            E2010 (2000-10), E2020 (2010-20)

    Raw data: D:\\PROJELER\\ghsl_raw\\{epoch}\\*.tif  (100m Mollweide)
    """
    import rasterio
    from rasterio.sample import sample_gen
    import geopandas as gpd
    from pyproj import Transformer

    if raw_path is None:
        raw_path = Path(r"D:\PROJELER\ghsl_raw")

    # Ordered epochs: earliest first → first non-zero = first built
    EPOCHS = [
        ("E1975", 1967),
        ("E1990", 1982),
        ("E2000", 1995),
        ("E2010", 2005),
        ("E2020", 2015),
    ]

    # Load all rasters keyed by epoch
    rasters = {}
    for epoch, year in EPOCHS:
        epoch_dir = raw_path / epoch
        tifs = list(epoch_dir.glob("*.tif")) if epoch_dir.exists() else []
        rasters[epoch] = tifs

    if not any(rasters.values()):
        print(f"ERROR: No GHSL .tif files found in {raw_path}")
        print("  Run: python ml/download_ghsl.py")
        return

    for city in cities:
        print(f"\n=== GHSL enrichment: {city} ===")
        osm = load_geojson(city)
        gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
        centroids = [(geom.centroid.x, geom.centroid.y) for geom in gdf.geometry]
        n = len(centroids)

        # Skip buildings that already have construction_year
        needs_year = [i for i, f in enumerate(osm["features"])
                      if not f["properties"].get("construction_year")]
        print(f"  Buildings needing year: {len(needs_year)} / {n}")

        if not needs_year:
            print("  All buildings already have year, skipping")
            continue

        # first_built[i] = year for building i, or None
        first_built = [None] * n

        for epoch, year in EPOCHS:
            tifs = rasters[epoch]
            if not tifs:
                print(f"  WARNING: No tiles for {epoch}, skipping")
                continue

            remaining = [i for i in needs_year if first_built[i] is None]
            if not remaining:
                break

            # Sample all tiles for this epoch; buildings covered by multiple tiles
            # will be sampled by the first matching tile
            remaining_coords = [centroids[i] for i in remaining]
            epoch_vals = [None] * len(remaining)

            for tif in tifs:
                with rasterio.open(tif) as src:
                    transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
                    proj = [transformer.transform(lon, lat) for lon, lat in remaining_coords]
                    sampled = list(sample_gen(src, proj))
                    for j, val in enumerate(sampled):
                        if epoch_vals[j] is None and val[0] and val[0] > 0:
                            epoch_vals[j] = year

            filled = sum(1 for v in epoch_vals if v is not None)
            print(f"  {epoch}: filled {filled} buildings")
            for j, i in enumerate(remaining):
                if epoch_vals[j] is not None:
                    first_built[i] = epoch_vals[j]

        # Write ghsl_neighborhood_year as a feature field (NOT construction_year)
        # GHSL tracks when the urban fabric was established, not individual building age.
        # Use as model input feature; construction_year labels come from PLUTO/OSM/open-data.
        updated = 0
        for i, feat in enumerate(osm["features"]):
            props = feat["properties"]
            props.setdefault("data_source", "OSM")
            if first_built[i]:
                props["ghsl_neighborhood_year"] = first_built[i]
                updated += 1

        print(f"  Added ghsl_neighborhood_year to {updated} buildings")
        stats(osm, f"{city} after GHSL")
        save_geojson(city, osm)

# ── Paris DPE ────────────────────────────────────────────────────────────────

def enrich_paris_dpe() -> None:
    """
    Enrich Paris buildings with construction_year from France DPE (Diagnostic de
    Performance Energétique) open dataset.

    Source: data.ademe.fr — 815K Paris records, field: periode_construction
    Period strings → midpoint year for spatial join to OSM footprints.
    """
    import geopandas as gpd
    import pandas as pd
    import urllib.request, json

    print("\n=== Paris DPE enrichment ===")

    PERIOD_TO_YEAR = {
        "avant 1948": 1920, "1948-1974": 1961, "1975-1977": 1976,
        "1978-1982": 1980, "1983-1988": 1985, "1989-2000": 1994,
        "2001-2005": 2003, "2006-2012": 2009, "2013-2021": 2017,
        "2021 et plus": 2022,
    }

    osm = load_geojson("paris")
    osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
    bbox = osm_gdf.total_bounds  # minx, miny, maxx, maxy

    # Fetch DPE points within bbox — paginate in chunks of 1000
    base = "https://data.ademe.fr/data-fair/api/v1/datasets/meg-83tjwtg8dyz4vv7h1dqe/lines"
    params = (
        f"?size=10000&select=periode_construction,_geopoint"
        f"&qs=code_departement_ban:75"
        f"&bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    )
    print(f"  Fetching DPE points for bbox {bbox.round(3)}...")
    rows = []
    skip = 0
    while True:
        url = base + params + f"&after={skip}" if skip else base + params
        try:
            resp = urllib.request.urlopen(url, timeout=30)
            data = json.loads(resp.read())
        except Exception as e:
            print(f"  Fetch error: {e}")
            break
        results = data.get("results", [])
        rows.extend(results)
        total = data.get("total", 0)
        print(f"  Fetched {len(rows)}/{total}")
        if len(rows) >= total or not results:
            break
        skip += len(results)

    if not rows:
        print("  ERROR: No DPE records fetched")
        return

    # Build GeoDataFrame from points
    pts = []
    for r in rows:
        gp = r.get("_geopoint", "")
        period = r.get("periode_construction", "")
        year = PERIOD_TO_YEAR.get(period)
        if not gp or not year:
            continue
        try:
            lat, lon = map(float, gp.split(","))
            pts.append({"geometry": __import__("shapely.geometry", fromlist=["Point"]).Point(lon, lat), "year": year})
        except Exception:
            continue

    dpe_gdf = gpd.GeoDataFrame(pts, crs="EPSG:4326")
    print(f"  Valid DPE points: {len(dpe_gdf)}")

    # Spatial join: each OSM building centroid → nearest DPE point (max 100m)
    osm_cents = osm_gdf.copy()
    osm_cents.geometry = osm_cents.geometry.centroid
    joined = gpd.sjoin_nearest(osm_cents, dpe_gdf[["geometry", "year"]], how="left", max_distance=0.001)

    updated = 0
    for i, feat in enumerate(osm["features"]):
        props = feat["properties"]
        if props.get("construction_year"):
            props.setdefault("data_source", "OSM")
            continue
        year = joined.iloc[i]["year"] if i < len(joined) else None
        if year and not pd.isna(year):
            props["construction_year"] = int(year)
            props["data_source"] = "Paris_DPE"
            updated += 1

    print(f"  Updated {updated} buildings")
    stats(osm, "paris after DPE")
    save_geojson("paris", osm)


# ── Wien Open Data ────────────────────────────────────────────────────────────

def enrich_wien_bauperiode() -> None:
    """
    Enrich Vienna buildings with construction_year from Wien Open Data WFS.

    Source: data.wien.gv.at — BAUPERIODEDETAILOGD layer
    OBJ_STR_TXT: "1884-1918" → midpoint year.
    438K building polygons, spatial join to OSM footprints.
    """
    import geopandas as gpd

    print("\n=== Wien BAUPERIODE enrichment ===")

    osm = load_geojson("vienna")
    osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
    bbox = osm_gdf.total_bounds
    bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

    WFS = (
        "https://data.wien.gv.at/daten/geo"
        "?service=WFS&version=1.1.0&request=GetFeature"
        "&typeName=ogdwien:BAUPERIODEDETAILOGD"
        f"&BBOX={bbox_str},EPSG:4326"
        "&outputFormat=application/json"
    )
    print(f"  Fetching Wien BAUPERIODE (bbox filtered)...")
    try:
        resp = __import__("urllib.request", fromlist=["urlopen"]).urlopen(WFS, timeout=60)
        wien = gpd.read_file(resp)
    except Exception as e:
        print(f"  WFS error: {e}")
        return

    print(f"  Wien features: {len(wien)}")
    wien = wien[["geometry", "OBJ_STR_TXT"]].dropna(subset=["OBJ_STR_TXT"])
    wien = wien.to_crs("EPSG:4326")

    def parse_period(s):
        import re
        years = re.findall(r"\d{4}", str(s))
        if not years:
            return None
        nums = [int(y) for y in years if 1800 <= int(y) <= 2025]
        return sum(nums) // len(nums) if nums else None

    wien["year"] = wien["OBJ_STR_TXT"].apply(parse_period)
    wien = wien.dropna(subset=["year"])
    print(f"  Parsed years: {len(wien)}")

    osm_cents = osm_gdf.copy()
    osm_cents.geometry = osm_cents.geometry.centroid
    joined = gpd.sjoin_nearest(osm_cents, wien[["geometry", "year"]], how="left", max_distance=0.001)

    updated = 0
    import pandas as pd
    for i, feat in enumerate(osm["features"]):
        props = feat["properties"]
        if props.get("construction_year"):
            props.setdefault("data_source", "OSM")
            continue
        year = joined.iloc[i]["year"] if i < len(joined) else None
        if year and not pd.isna(year):
            props["construction_year"] = int(year)
            props["data_source"] = "Wien_OD"
            updated += 1

    print(f"  Updated {updated} buildings")
    stats(osm, "vienna after Wien OD")
    save_geojson("vienna", osm)


# ── Chicago Building Permits ──────────────────────────────────────────────────

def enrich_chicago_permits() -> None:
    """
    Enrich Chicago buildings with construction_year from Chicago Data Portal
    'NEW CONSTRUCTION' building permits (31K records with lat/lon + issue_date).

    Source: data.cityofchicago.org — resource ydr8-5enu
    """
    import geopandas as gpd
    import pandas as pd
    import urllib.request, json
    from shapely.geometry import Point

    print("\n=== Chicago building permits enrichment ===")

    osm = load_geojson("chicago")
    osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")
    bbox = osm_gdf.total_bounds

    import urllib.parse
    BASE = "https://data.cityofchicago.org/resource/ydr8-5enu.json"
    where = (
        f"permit_type like '%NEW CONSTRUCTION%'"
        f" AND latitude IS NOT NULL"
        f" AND latitude > {bbox[1]} AND latitude < {bbox[3]}"
        f" AND longitude > {bbox[0]} AND longitude < {bbox[2]}"
    )
    params = urllib.parse.urlencode({
        "$limit": 50000,
        "$where": where,
        "$select": "issue_date,latitude,longitude",
    })
    print("  Fetching Chicago new construction permits...")
    resp = urllib.request.urlopen(BASE + "?" + params, timeout=30)
    rows = json.loads(resp.read())
    print(f"  Got {len(rows)} permits")

    pts = []
    for r in rows:
        try:
            year = int(r["issue_date"][:4])
            lat, lon = float(r["latitude"]), float(r["longitude"])
            pts.append({"geometry": Point(lon, lat), "year": year})
        except Exception:
            continue
    permits_gdf = gpd.GeoDataFrame(pts, crs="EPSG:4326")

    osm_cents = osm_gdf.copy()
    osm_cents.geometry = osm_cents.geometry.centroid
    joined = gpd.sjoin_nearest(osm_cents, permits_gdf[["geometry", "year"]], how="left", max_distance=0.001)

    updated = 0
    for i, feat in enumerate(osm["features"]):
        props = feat["properties"]
        if props.get("construction_year"):
            props.setdefault("data_source", "OSM")
            continue
        year = joined.iloc[i]["year"] if i < len(joined) else None
        if year and not pd.isna(year):
            props["construction_year"] = int(year)
            props["data_source"] = "Chicago_Permits"
            updated += 1

    print(f"  Updated {updated} buildings")
    stats(osm, "chicago after permits")
    save_geojson("chicago", osm)


# ── OSM start_date fallback (all cities) ──────────────────────────────────────

def enrich_osm_start_date(cities: list[str]) -> None:
    """
    Fetch buildings with start_date tag from Overpass API for cities with poor coverage.
    Covers Barcelona (528), Tokyo (389), London (236+), and others.
    Spatial join to OSM footprints by centroid proximity.
    """
    import geopandas as gpd
    import pandas as pd
    import urllib.request, urllib.parse, json
    from shapely.geometry import Point

    CITY_BBOX = {
        "barcelona": (41.30, 2.08, 41.50, 2.26),
        "tokyo":     (35.62, 139.67, 35.75, 139.82),
        "london":    (51.47, -0.15, 51.53, 0.00),
        "madrid":    (40.38, -3.75, 40.47, -3.62),
        "istanbul":  (40.97, 28.88, 41.08, 29.06),
        "moscow":    (55.71, 37.55, 55.80, 37.68),
        "chicago":   (41.83, -87.70, 41.92, -87.58),
    }

    OVERPASS = "https://overpass-api.de/api/interpreter"

    for city in cities:
        if city not in CITY_BBOX:
            continue
        print(f"\n=== OSM start_date enrichment: {city} ===")
        osm = load_geojson(city)
        osm_gdf = gpd.GeoDataFrame.from_features(osm["features"], crs="EPSG:4326")

        s, w, n, e = CITY_BBOX[city]
        query = f'[out:json][timeout:30];way["building"]["start_date"]({s},{w},{n},{e});out body center qt;'
        try:
            body = urllib.parse.urlencode({"data": query}).encode("utf-8")
            req = urllib.request.Request(
                OVERPASS,
                data=body,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "User-Agent": "ChronoCity/1.0",
                },
            )
            resp = urllib.request.urlopen(req, timeout=35)
            data = json.loads(resp.read())
        except Exception as ex:
            print(f"  Overpass error: {ex}")
            continue

        elements = data.get("elements", [])
        print(f"  OSM buildings with start_date: {len(elements)}")

        pts = []
        for el in elements:
            raw = el.get("tags", {}).get("start_date", "")
            try:
                year = int(str(raw)[:4])
                if not (1700 <= year <= 2025):
                    continue
                center = el.get("center", {})
                if not center:
                    continue
                pts.append({"geometry": Point(center["lon"], center["lat"]), "year": year})
            except Exception:
                continue

        if not pts:
            print("  No valid points, skipping")
            continue

        src_gdf = gpd.GeoDataFrame(pts, crs="EPSG:4326")
        osm_cents = osm_gdf.copy()
        osm_cents.geometry = osm_cents.geometry.centroid
        joined = gpd.sjoin_nearest(osm_cents, src_gdf[["geometry", "year"]], how="left", max_distance=0.0005)

        updated = 0
        for i, feat in enumerate(osm["features"]):
            props = feat["properties"]
            if props.get("construction_year"):
                props.setdefault("data_source", "OSM")
                continue
            year = joined.iloc[i]["year"] if i < len(joined) else None
            if year and not pd.isna(year):
                props["construction_year"] = int(year)
                props["data_source"] = "OSM_start_date"
                updated += 1

        print(f"  Updated {updated} buildings")
        stats(osm, f"{city} after OSM start_date")
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
    parser.add_argument("--source", choices=["pluto", "geoportal", "ghsl", "paris-dpe", "wien-od", "chicago-permits", "osm-start-date", "mark-osm", "all"], default="pluto")
    parser.add_argument("--raw",    help="Override raw data directory path")
    args = parser.parse_args()

    cities = ALL_CITIES if args.city == "all" else [args.city]
    raw = Path(args.raw) if args.raw else None

    if args.source in ("pluto", "all") and "new-york" in cities:
        enrich_nyc_pluto(raw)

    if args.source in ("geoportal", "all") and "berlin" in cities:
        enrich_berlin_geoportal(raw)

    if args.source in ("ghsl", "all"):
        ghsl_cities = ALL_CITIES if args.source == "all" else cities
        enrich_ghsl(ghsl_cities, raw)

    if args.source in ("paris-dpe", "all"):
        enrich_paris_dpe()

    if args.source in ("wien-od", "all"):
        enrich_wien_bauperiode()

    if args.source in ("chicago-permits", "all") and "chicago" in cities:
        enrich_chicago_permits()

    if args.source in ("osm-start-date", "all"):
        osm_cities = [c for c in cities if c not in ("new-york", "paris", "vienna", "berlin")]
        enrich_osm_start_date(osm_cities)

    if args.source == "mark-osm":
        for city in cities:
            mark_osm_source(city)

if __name__ == "__main__":
    main()
