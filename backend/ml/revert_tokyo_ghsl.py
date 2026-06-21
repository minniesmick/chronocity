"""Remove wrong construction_year values added by GHSL (should be ghsl_neighborhood_year)."""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
cities = ["tokyo", "istanbul", "barcelona", "madrid", "chicago", "london", "vienna", "moscow", "paris", "berlin", "new-york"]

for city in cities:
    path = ROOT / "public" / "cities" / city / "buildings.geojson"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    reverted = 0
    for feat in data["features"]:
        props = feat["properties"]
        if props.get("data_source") == "GHSL":
            del props["construction_year"]
            props["data_source"] = "OSM"
            reverted += 1

    if reverted:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{city}: reverted {reverted} buildings")
    else:
        print(f"{city}: clean, no revert needed")
