"""
Building polygon downloader via Overpass API.

Usage:
  python download_buildings.py --city istanbul --bbox 28.85,40.95,29.12,41.08
  python download_buildings.py --city istanbul  # uses preset bbox

Writes output to public/cities/{city}/buildings.geojson
Existing file is backed up to buildings.geojson.bak before overwrite.
"""

import argparse
import json
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
PUBLIC = ROOT / "public" / "cities"

OVERPASS = "https://overpass-api.de/api/interpreter"

# [west, south, east, north] — WGS84
PRESET_BBOX = {
    "istanbul":  [28.85, 40.95, 29.12, 41.08],
    "new-york":  [-74.06, 40.68, -73.90, 40.82],
    "chicago":   [-87.72, 41.82, -87.55, 41.95],
    "berlin":    [13.32, 52.46, 13.52, 52.58],
    "vienna":    [16.29, 48.15, 16.46, 48.27],
    "paris":     [2.28,  48.80, 2.44,  48.92],
    "london":    [-0.18, 51.46, 0.02,  51.57],
    "barcelona": [2.10,  41.32, 2.26,  41.46],
    "madrid":    [-3.78, 40.36, -3.60, 40.48],
    "tokyo":     [139.65, 35.61, 139.84, 35.76],
    "moscow":    [37.52, 55.70, 37.72, 55.82],
}


def fetch_overpass(query: str, timeout: int = 120) -> dict:
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "User-Agent": "ChronoCity/1.0 building-downloader",
        },
    )
    resp = urllib.request.urlopen(req, timeout=timeout + 10)
    return json.loads(resp.read())


def parse_height(tags: dict) -> float | None:
    """Extract numeric height in metres from OSM tags."""
    for key in ("height", "building:height"):
        raw = tags.get(key)
        if raw:
            try:
                return float(str(raw).replace("m", "").strip())
            except ValueError:
                pass
    # Estimate from levels
    levels = tags.get("building:levels") or tags.get("levels")
    if levels:
        try:
            return round(float(levels) * 3.2, 1)
        except ValueError:
            pass
    return None


def parse_year(tags: dict) -> int | None:
    """Extract construction year from OSM tags."""
    for key in ("start_date", "construction_date", "building:start_date"):
        raw = tags.get(key)
        if raw:
            try:
                year = int(str(raw)[:4])
                if 1700 <= year <= 2025:
                    return year
            except ValueError:
                pass
    return None


def nodes_to_coords(node_ids: list[int], node_map: dict[int, tuple]) -> list | None:
    """Convert list of node IDs to coordinate ring."""
    ring = []
    for nid in node_ids:
        if nid not in node_map:
            return None
        ring.append(list(node_map[nid]))
    return ring


def existing_bbox(features: list[dict]) -> tuple[float, float, float, float] | None:
    """Return (west, south, east, north) of existing features."""
    lons, lats = [], []
    for f in features:
        g = f.get("geometry", {})
        if g.get("type") == "Polygon":
            for ring in g["coordinates"]:
                for c in ring:
                    lons.append(c[0])
                    lats.append(c[1])
    if not lons:
        return None
    return min(lons), min(lats), max(lons), max(lats)


def download_city(city: str, bbox: list[float], chunk_size: float = 0.08) -> None:
    west, south, east, north = bbox
    out_path = PUBLIC / city / "buildings.geojson"
    bak_path = PUBLIC / city / "buildings.geojson.bak"

    # Load existing data — keep enriched buildings, track their IDs via geometry hash
    existing_features: list[dict] = []
    seen_way_ids: set[int] = set()

    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            existing = json.load(f)
        existing_features = existing.get("features", [])
        ex_bbox = existing_bbox(existing_features)
        if ex_bbox:
            ex_w, ex_s, ex_e, ex_n = ex_bbox
            print(f"Existing: {len(existing_features)} buildings, bbox [{ex_w:.4f},{ex_s:.4f},{ex_e:.4f},{ex_n:.4f}]")
            print(f"Target  : [{west:.4f},{south:.4f},{east:.4f},{north:.4f}]")

            # Build delta chunks — only areas OUTSIDE existing bbox
            # We split the target bbox into regions not covered by existing
            delta_regions = []
            if south < ex_s:   delta_regions.append((west,  south, east,  ex_s))   # south strip
            if north > ex_n:   delta_regions.append((west,  ex_n,  east,  north))  # north strip
            if west  < ex_w:   delta_regions.append((west,  ex_s,  ex_w,  ex_n))   # west strip
            if east  > ex_e:   delta_regions.append((ex_e,  ex_s,  east,  ex_n))   # east strip

            if not delta_regions:
                print("Target bbox already covered by existing data. Nothing to download.")
                return

            print(f"Delta regions to download: {len(delta_regions)}")
        else:
            delta_regions = [(west, south, east, north)]
    else:
        existing_features = []
        delta_regions = [(west, south, east, north)]
        print(f"No existing file — full download for {city}")

    # Chunk each delta region
    chunks = []
    for rw, rs, re, rn in delta_regions:
        lon_steps = [rw + i * chunk_size for i in range(int((re - rw) / chunk_size) + 1)]
        lat_steps = [rs + i * chunk_size for i in range(int((rn - rs) / chunk_size) + 1)]
        for lx in lon_steps:
            for ly in lat_steps:
                cw, cs, ce, cn = max(rw, lx), max(rs, ly), min(re, lx + chunk_size), min(rn, ly + chunk_size)
                if cw < ce and cs < cn:
                    chunks.append((cw, cs, ce, cn))

    all_features: list[dict] = list(existing_features)

    print(f"Downloading {city}: {len(chunks)} chunk(s) (delta only)")

    for i, (cw, cs, ce, cn) in enumerate(chunks):
        print(f"  Chunk {i+1}/{len(chunks)}: [{cs:.3f},{cw:.3f},{cn:.3f},{ce:.3f}]")
        query = (
            f"[out:json][timeout:90];"
            f"way[\"building\"]({cs},{cw},{cn},{ce});"
            f"(._;>;);"
            f"out body qt;"
        )
        try:
            data = fetch_overpass(query, timeout=90)
        except Exception as e:
            print(f"    ERROR: {e} — skipping chunk")
            time.sleep(3)
            continue

        elements = data.get("elements", [])
        node_map: dict[int, tuple] = {}
        ways: list[dict] = []

        for el in elements:
            if el["type"] == "node":
                node_map[el["id"]] = (el["lon"], el["lat"])
            elif el["type"] == "way" and el["id"] not in seen_way_ids:
                ways.append(el)
                seen_way_ids.add(el["id"])

        for way in ways:
            nds = way.get("nodes", [])
            ring = nodes_to_coords(nds, node_map)
            if not ring or len(ring) < 4:
                continue
            tags = way.get("tags", {})
            feature = {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [ring]},
                "properties": {
                    "height": parse_height(tags),
                    "construction_year": parse_year(tags),
                    "name": tags.get("name"),
                    "data_source": "OSM",
                    "ghsl_neighborhood_year": None,
                },
            }
            all_features.append(feature)

        print(f"    → {len(ways)} buildings (total so far: {len(all_features)})")
        time.sleep(1.2)  # Overpass rate limit courtesy

    if not all_features:
        print("No features downloaded — aborting, existing file kept.")
        return

    # Backup existing
    if out_path.exists():
        shutil.copy(out_path, bak_path)
        print(f"Backed up existing → {bak_path}")

    geojson = {"type": "FeatureCollection", "features": all_features}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nDone. {len(all_features)} buildings → {out_path}")
    print("Next: run enrich_buildings.py to add construction_year + ghsl_neighborhood_year")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", required=True, help="City id (e.g. istanbul)")
    parser.add_argument(
        "--bbox",
        help="west,south,east,north (overrides preset)",
    )
    args = parser.parse_args()

    if args.bbox:
        bbox = [float(x) for x in args.bbox.split(",")]
        assert len(bbox) == 4, "bbox must be: west,south,east,north"
    elif args.city in PRESET_BBOX:
        bbox = PRESET_BBOX[args.city]
    else:
        raise SystemExit(f"No preset for '{args.city}'. Pass --bbox west,south,east,north")

    download_city(args.city, bbox)
