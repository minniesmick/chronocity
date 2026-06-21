"""Find which GHSL tiles cover our 11 cities, then download them."""
from pyproj import Transformer
import urllib.request, os, pathlib

# City centers [lon, lat]
CITIES = {
    "new-york":  (-73.988, 40.748),
    "chicago":   (-87.628, 41.878),
    "berlin":    (13.405,  52.520),
    "vienna":    (16.373,  48.208),
    "paris":     (2.352,   48.856),
    "london":    (-0.080,  51.505),
    "barcelona": (2.164,   41.389),
    "madrid":    (-3.695,  40.416),
    "moscow":    (37.617,  55.755),
    "istanbul":  (28.965,  41.013),
    "tokyo":     (139.745, 35.690),
}

# GHSL Mollweide tile grid parameters (from JRC docs)
# Global extent: X [-18036000, 18036000], Y [9000000, -9000000]
# Tile size: 1,000,000m each → 36 cols, 18 rows
TILE_SIZE = 1_000_000
X_MIN, Y_MAX = -18_036_000, 9_000_000

transformer = Transformer.from_crs("EPSG:4326", "ESRI:54009", always_xy=True)

needed_tiles = set()
print("City → Mollweide → Tile:")
for city, (lon, lat) in CITIES.items():
    mx, my = transformer.transform(lon, lat)
    col = int((mx - X_MIN) / TILE_SIZE) + 1
    row = int((Y_MAX - my) / TILE_SIZE) + 1
    tile = f"R{row}_C{col}"
    needed_tiles.add(tile)
    print(f"  {city:12} → ({mx:10.0f}, {my:9.0f}) → {tile}")

print(f"\nUnique tiles needed: {sorted(needed_tiles)}")

# Verify which tiles exist
BASE = "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_C_GLOBE_R2023A/GHS_BUILT_C_MSZ_E2018_GLOBE_R2023A_54009_10/V1-0/tiles"

print("\nVerifying tiles exist:")
valid = []
for tile in sorted(needed_tiles):
    url = f"{BASE}/GHS_BUILT_C_MSZ_E2018_GLOBE_R2023A_54009_10_V1_0_{tile}.zip"
    try:
        r = urllib.request.urlopen(url, timeout=8)
        size_mb = int(r.headers.get("Content-Length", 0)) // 1_048_576
        print(f"  {tile}: OK ({size_mb} MB) → {url}")
        valid.append((tile, url, size_mb))
    except Exception as e:
        print(f"  {tile}: NOT FOUND ({e})")

print(f"\nTotal download: ~{sum(s for _,_,s in valid)} MB across {len(valid)} tiles")
