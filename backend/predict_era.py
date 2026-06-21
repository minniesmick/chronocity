"""
ML-3: Building era prediction endpoint helpers.
Loaded by main FastAPI app.
"""

import pickle
import json
import math
from pathlib import Path
from typing import Optional

import numpy as np

BACKEND = Path(__file__).parent
MODEL_PATH = BACKEND / "era_model.pkl"

ERA_NAMES = ["Tas_Barok", "Grunderzeit", "Art_Deco", "Brutalizm", "Prefab", "Cam_Celik", "Modern"]
ERA_LABELS = {
    0: {"name": "Taş/Barok", "period": "< 1870", "color": "#8B4513"},
    1: {"name": "Gründerzeit", "period": "1870–1918", "color": "#C19A6B"},
    2: {"name": "Art Deco", "period": "1918–1945", "color": "#DAA520"},
    3: {"name": "Brutalizm", "period": "1945–1965", "color": "#708090"},
    4: {"name": "Prefab", "period": "1965–1980", "color": "#CD853F"},
    5: {"name": "Cam & Çelik", "period": "1980–2000", "color": "#4682B4"},
    6: {"name": "Modern", "period": "≥ 2000", "color": "#2E8B57"},
}

CITY_CENTERS = {
    "new-york":  (-73.988, 40.748),
    "paris":     (2.352,   48.856),
    "vienna":    (16.373,  48.208),
    "chicago":   (-87.628, 41.878),
    "berlin":    (13.405,  52.520),
    "moscow":    (37.617,  55.755),
    "london":    (-0.080,  51.505),
    "barcelona": (2.164,   41.389),
    "madrid":    (-3.695,  40.416),
    "tokyo":     (139.745, 35.690),
    "istanbul":  (28.965,  41.013),
}

FEATURE_COLS = [
    "area_m2", "perimeter_m", "compactness", "aspect_ratio", "n_vertices",
    "height", "dist_to_center_km", "ghsl_neighborhood_year",
    "neighbor_mean_height", "building_density_200m", "lat", "lon",
]

_model = None

def get_model():
    global _model
    if _model is None:
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
    return _model


def haversine_km(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def predict_single(
    city: str,
    lon: float,
    lat: float,
    area_m2: float = 0.0,
    perimeter_m: float = 0.0,
    compactness: float = 0.5,
    aspect_ratio: float = 1.5,
    n_vertices: int = 4,
    height: float = 0.0,
    ghsl_neighborhood_year: Optional[float] = None,
    neighbor_mean_height: float = 0.0,
    building_density_200m: int = 10,
) -> dict:
    cx, cy = CITY_CENTERS.get(city, (lon, lat))
    dist = haversine_km(lon, lat, cx, cy)

    import pandas as pd
    row = pd.DataFrame([{
        "area_m2": area_m2, "perimeter_m": perimeter_m,
        "compactness": compactness, "aspect_ratio": aspect_ratio,
        "n_vertices": n_vertices, "height": height,
        "dist_to_center_km": dist,
        "ghsl_neighborhood_year": ghsl_neighborhood_year or 1990.0,
        "neighbor_mean_height": neighbor_mean_height,
        "building_density_200m": building_density_200m,
        "lat": lat, "lon": lon,
    }])

    model = get_model()
    era_idx = int(model.predict(row)[0])
    proba = model.predict_proba(row)[0].tolist()

    return {
        "era": era_idx,
        "era_name": ERA_LABELS[era_idx]["name"],
        "era_period": ERA_LABELS[era_idx]["period"],
        "era_color": ERA_LABELS[era_idx]["color"],
        "confidence": float(max(proba)),
        "probabilities": {ERA_LABELS[i]["name"]: round(p, 4) for i, p in enumerate(proba)},
    }


def predict_batch(buildings: list[dict], city: str) -> list[dict]:
    """Predict era for a list of building feature dicts."""
    model = get_model()
    cx, cy = CITY_CENTERS.get(city, (0, 0))

    import pandas as pd
    col_map = {
        "dist_to_center_km": lambda b, cx, cy: haversine_km(b.get("lon", 0), b.get("lat", 0), cx, cy),
    }
    records = []
    for b in buildings:
        lon_, lat_ = b.get("lon", 0), b.get("lat", 0)
        dist = haversine_km(lon_, lat_, cx, cy)
        records.append({
            "area_m2": b.get("area_m2", 0), "perimeter_m": b.get("perimeter_m", 0),
            "compactness": b.get("compactness", 0.5), "aspect_ratio": b.get("aspect_ratio", 1.5),
            "n_vertices": b.get("n_vertices", 4), "height": b.get("height", 0),
            "dist_to_center_km": dist,
            "ghsl_neighborhood_year": b.get("ghsl_neighborhood_year", 1990),
            "neighbor_mean_height": b.get("neighbor_mean_height", 0),
            "building_density_200m": b.get("building_density_200m", 10),
            "lat": lat_, "lon": lon_,
        })
    X = pd.DataFrame(records)
    era_idxs = model.predict(X).tolist()
    probas = model.predict_proba(X).tolist()

    results = []
    for i, (era_idx, proba) in enumerate(zip(era_idxs, probas)):
        era_idx = int(era_idx)
        results.append({
            **buildings[i],
            "predicted_era": era_idx,
            "predicted_era_name": ERA_LABELS[era_idx]["name"],
            "predicted_era_color": ERA_LABELS[era_idx]["color"],
            "confidence": round(float(max(proba)), 4),
        })
    return results
