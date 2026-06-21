"""
Berlin ALKIS building data (Baujahr/construction year) downloader.
Tries multiple known endpoints, falls back to manual instruction.
"""
import ssl, urllib.request, json, pathlib, sys

OUT = pathlib.Path(__file__).parent / "data" / "raw" / "berlin_geoportal"
OUT.mkdir(parents=True, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Known Berlin WFS endpoints for buildings with Baujahr
ENDPOINTS = [
    # ALKIS buildings via FIS-Broker
    "https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/s_wfs_alkis_gebaeude?service=WFS&version=2.0.0&request=GetFeature&typeNames=s_wfs_alkis_gebaeude&outputFormat=application/json&count=100",
    # Alternative: ISU block map
    "https://fbinter.stadt-berlin.de/fb/wfs/geometry/senstadt/re_gebaeude?service=WFS&version=2.0.0&request=GetFeature&outputFormat=application/json&count=100",
]

for url in ENDPOINTS:
    print(f"Trying: {url[:80]}...")
    try:
        req = urllib.request.urlopen(url, timeout=20, context=ctx)
        data = req.read()
        parsed = json.loads(data)
        features = parsed.get("features", [])
        print(f"  OK — {len(features)} features")
        if features:
            cols = list(features[0].get("properties", {}).keys())
            print(f"  Columns: {cols}")
            year_col = next((c for c in cols if "bau" in c.lower() or "year" in c.lower()), None)
            print(f"  Year column: {year_col}")
    except Exception as e:
        print(f"  FAILED: {e}")

print("\n--- Manual download fallback ---")
print("1. Open: https://daten.berlin.de/datensaetze/gebaude-berlin-wfs")
print("2. OR:   https://www.stadtentwicklung.berlin.de/geoinformation/fis-broker/")
print("3. Search: 'Gebaeude Baujahr' or 'ALKIS Gebaeude'")
print("4. Download as GeoJSON or Shapefile")
print(f"5. Save to: {OUT}")
print("6. Run: python backend/ml/enrich_buildings.py --city berlin --source geoportal")
