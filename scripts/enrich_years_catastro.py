"""
Catastro INSPIRE WFS -> construction_year enrichment for Madrid & Barcelona.
Fetches in grid tiles to avoid timeouts.
"""

import json
import math
import re
import sys
import time

import requests
import urllib3

urllib3.disable_warnings()

WFS = "https://ovc.catastro.meh.es/INSPIRE/wfsBU.aspx"
CITIES = {
    "madrid":    (40.37, -3.74, 40.46, -3.64),
    "barcelona": (41.35,  2.12, 41.43,  2.22),
}
BUILDINGS_DIR = r"C:\Users\alper\PROJELER\chronocity\public\cities"
THRESHOLD_DEG = 0.00015   # ~15m
TILE_STEP     = 0.01      # ~1km tiles to avoid server timeout
REQUEST_DELAY = 12        # seconds between tile requests (server rate limit)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Accept": "application/xml, text/xml, */*; q=0.01",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Namespace constants from actual server response
NS_CORE = "http://inspire.jrc.ec.europa.eu/schemas/bu-core2d/2.0"
NS_EXT  = "http://inspire.jrc.ec.europa.eu/schemas/bu-ext2d/2.0"
NS_GML  = "http://www.opengis.net/gml/3.2"


def fetch_tile(min_lat, min_lon, max_lat, max_lon, retry=3):
    """Fetch buildings for one small tile. Returns list of (lon, lat, year)."""
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": "BU.Building",
        "count": "5000",
        "srsName": "EPSG:4326",
        "bbox": f"{min_lat},{min_lon},{max_lat},{max_lon},EPSG:4326",
    }
    for attempt in range(retry):
        try:
            r = requests.get(WFS, params=params, headers=HEADERS, timeout=45, verify=False)
            r.raise_for_status()
            return parse_xml(r.content.decode("latin-1"))
        except Exception as e:
            wait = REQUEST_DELAY * (attempt + 1)
            print(f"    Tile {min_lat:.3f},{min_lon:.3f} attempt {attempt+1} failed: {type(e).__name__}. Retrying in {wait}s...")
            time.sleep(wait)
    return []


# Regex approach — faster & avoids namespace hell
RE_YEAR    = re.compile(r"<bu-core2d:beginning>(\d{4})-")
RE_POSLIST = re.compile(r"<gml:posList[^>]*>([\d\s\.\-]+)</gml:posList>")
RE_BUILDING = re.compile(
    r"<bu-ext2d:Building[^>]*>(.*?)</bu-ext2d:Building>",
    re.DOTALL,
)


def parse_xml(text):
    results = []
    for m in RE_BUILDING.finditer(text):
        bldg = m.group(1)

        year_m = RE_YEAR.search(bldg)
        if not year_m:
            continue
        year = int(year_m.group(1))

        pos_m = RE_POSLIST.search(bldg)
        if not pos_m:
            continue
        vals = list(map(float, pos_m.group(1).split()))
        if len(vals) < 4:
            continue

        # Catastro posList: lat lon lat lon ...
        lats = vals[0::2]
        lons = vals[1::2]
        lat = sum(lats) / len(lats)
        lon = sum(lons) / len(lons)
        results.append((lon, lat, year))

    return results


def geojson_centroid(feature):
    geom = feature["geometry"]
    t = geom["type"]
    ring = None
    if t == "Polygon":
        ring = geom["coordinates"][0]
    elif t == "MultiPolygon":
        ring = geom["coordinates"][0][0]
    if not ring:
        return None
    xs = [c[0] for c in ring]
    ys = [c[1] for c in ring]
    return sum(xs) / len(xs), sum(ys) / len(ys)   # (lon, lat)


def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def enrich_city(city_id, bbox):
    min_lat, min_lon, max_lat, max_lon = bbox
    path = rf"{BUILDINGS_DIR}\{city_id}\buildings.geojson"

    with open(path, encoding="utf-8") as f:
        gj = json.load(f)

    features = gj["features"]
    missing_before = sum(1 for f in features if not f["properties"].get("construction_year"))
    print(f"\n{city_id}: {len(features)} bina, {missing_before} eksik yıl")

    # Find only tiles that contain buildings needing enrichment
    needed_tiles = set()
    for feat in features:
        if feat["properties"].get("construction_year"):
            continue
        c = geojson_centroid(feat)
        if c is None:
            continue
        flon, flat = c
        tile_lat = min_lat + math.floor((flat - min_lat) / TILE_STEP) * TILE_STEP
        tile_lon = min_lon + math.floor((flon - min_lon) / TILE_STEP) * TILE_STEP
        needed_tiles.add((round(tile_lat, 4), round(tile_lon, 4)))

    print(f"  {len(needed_tiles)} tile gerekli (toplam {int((max_lat-min_lat)/TILE_STEP)*int((max_lon-min_lon)/TILE_STEP)} tile yerine)")

    # Grid-tile Catastro fetch — only needed tiles
    catastro = []
    tiles_done = 0
    for tile_lat, tile_lon in sorted(needed_tiles):
        batch = fetch_tile(tile_lat, tile_lon,
                           min(tile_lat + TILE_STEP, max_lat),
                           min(tile_lon + TILE_STEP, max_lon))
        catastro.extend(batch)
        tiles_done += 1
        print(f"  tile ({tile_lat:.3f},{tile_lon:.3f}): {len(batch)} -> toplam {len(catastro)}")
        if tiles_done < len(needed_tiles):
            time.sleep(REQUEST_DELAY)

    print(f"  Catastro toplam yıllı bina: {len(catastro)}")
    if not catastro:
        return 0

    # Enrich
    filled = 0
    for feat in features:
        if feat["properties"].get("construction_year"):
            continue
        c = geojson_centroid(feat)
        if c is None:
            continue
        best = min(catastro, key=lambda p: dist2((p[0], p[1]), c))
        if math.sqrt(dist2((best[0], best[1]), c)) < THRESHOLD_DEG:
            feat["properties"]["construction_year"] = best[2]
            filled += 1

    print(f"  {filled} bina zenginleştirildi")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gj, f, ensure_ascii=False, separators=(",", ":"))
    return filled


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    total = 0
    for city_id, bbox in CITIES.items():
        if target != "all" and city_id != target:
            continue
        try:
            total += enrich_city(city_id, bbox)
        except Exception as e:
            print(f"HATA ({city_id}): {e}")
    print(f"\nToplam zenginleştirilen: {total}")
