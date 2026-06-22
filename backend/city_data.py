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