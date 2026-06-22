import json
from pathlib import Path
from fastapi import HTTPException


def get_project_root() -> Path:
    """
    backend/ klasöründen proje ana klasörüne çıkar.
    backend/city_data.py -> chronocity/
    """
    return Path(__file__).resolve().parents[1]


def get_city_geojson_path(city_id: str) -> Path:
    """
    public/cities/{city_id}/buildings.geojson yolunu döndürür.
    """
    return get_project_root() / "public" / "cities" / city_id / "buildings.geojson"


def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def safe_int(value):
    try:
        if value is None:
            return None
        return int(float(value))
    except (ValueError, TypeError):
        return None


def load_city_buildings(city_id: str) -> list[dict]:
    """
    Şehir GeoJSON dosyasını okur ve bina listesini normalize eder.
    """
    file_path = get_city_geojson_path(city_id)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Building data not found for city: {city_id}"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    buildings = []

    for index, feature in enumerate(geojson.get("features", [])):
        props = feature.get("properties", {}) or {}

        height = safe_float(
            props.get("height")
            or props.get("height_m")
            or props.get("building:height")
        )

        construction_year = safe_int(
            props.get("construction_year")
            or props.get("year_built")
            or props.get("start_date")
        )

        name = (
            props.get("name")
            or props.get("building_name")
            or "Unnamed Building"
        )

        building_id = (
            props.get("id")
            or props.get("osm_id")
            or props.get("fid")
            or props.get("@id")
            or index
        )

        buildings.append({
            "id": building_id,
            "name": name,
            "height": height,
            "construction_year": construction_year,
            "geometry": feature.get("geometry"),
            "properties": props,
        })

    return buildings

def list_available_cities() -> list[dict]:
    """
    Lists all cities that have a public/cities/{city_id}/buildings.geojson file.
    """

    cities_root = get_project_root() / "public" / "cities"

    if not cities_root.exists():
        return []

    cities = []

    for city_dir in sorted(cities_root.iterdir()):
        if not city_dir.is_dir():
            continue

        city_id = city_dir.name
        geojson_path = city_dir / "buildings.geojson"

        if not geojson_path.exists():
            continue

        try:
            buildings = load_city_buildings(city_id)
            total_buildings = len(buildings)

            year_count = len([
                b for b in buildings
                if isinstance(b.get("construction_year"), int)
            ])

            if total_buildings == 0:
                year_coverage_ratio = 0
            else:
                year_coverage_ratio = year_count / total_buildings

            if year_coverage_ratio >= 0.7:
                year_coverage = "strong"
            elif year_coverage_ratio >= 0.2:
                year_coverage = "medium"
            elif year_coverage_ratio > 0:
                year_coverage = "weak"
            else:
                year_coverage = "none"

            cities.append({
                "id": city_id,
                "name": city_id.replace("-", " ").title(),
                "has_building_data": True,
                "building_count": total_buildings,
                "buildings_with_construction_year": year_count,
                "year_coverage_ratio": round(year_coverage_ratio, 4),
                "year_coverage": year_coverage,
            })

        except Exception:
            cities.append({
                "id": city_id,
                "name": city_id.replace("-", " ").title(),
                "has_building_data": True,
                "building_count": None,
                "buildings_with_construction_year": None,
                "year_coverage_ratio": None,
                "year_coverage": "unknown",
            })

    return cities