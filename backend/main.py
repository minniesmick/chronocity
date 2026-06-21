"""ChronoCity backend — FastAPI.

Endpoints:
- GET  /api/health            → health check
- POST /api/predict-era       → single building era prediction
- POST /api/predict-era/batch → batch prediction (up to 1000 buildings)
- GET  /api/predict-city/{city} → predict all unlabeled buildings in a city
- WS   /ws                    → ephemeral broadcast (SoundNotePin — SPRINT 7)
"""
from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import numpy as np

app = FastAPI(title="ChronoCity API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "chronocity"}


# ── ML-3: Era Prediction ───────────────────────────────────────────────────────

class BuildingFeatures(BaseModel):
    city: str
    lon: float
    lat: float
    area_m2: float = 0.0
    perimeter_m: float = 0.0
    compactness: float = 0.5
    aspect_ratio: float = 1.5
    n_vertices: int = 4
    height: float = 0.0
    ghsl_neighborhood_year: Optional[float] = None
    neighbor_mean_height: float = 0.0
    building_density_200m: int = 10


class BuildingBatch(BaseModel):
    city: str
    buildings: list[BuildingFeatures] = Field(..., max_length=1000)


@app.post("/api/predict-era")
async def predict_era(feat: BuildingFeatures):
    try:
        from predict_era import predict_single
        result = predict_single(
            city=feat.city, lon=feat.lon, lat=feat.lat,
            area_m2=feat.area_m2, perimeter_m=feat.perimeter_m,
            compactness=feat.compactness, aspect_ratio=feat.aspect_ratio,
            n_vertices=feat.n_vertices, height=feat.height,
            ghsl_neighborhood_year=feat.ghsl_neighborhood_year,
            neighbor_mean_height=feat.neighbor_mean_height,
            building_density_200m=feat.building_density_200m,
        )
        return result
    except FileNotFoundError:
        raise HTTPException(503, "Model not loaded — run train_model.py first")


@app.post("/api/predict-era/batch")
async def predict_era_batch(payload: BuildingBatch):
    try:
        from predict_era import predict_batch
        buildings = [b.model_dump() for b in payload.buildings]
        return {"city": payload.city, "predictions": predict_batch(buildings, payload.city)}
    except FileNotFoundError:
        raise HTTPException(503, "Model not loaded — run train_model.py first")


@app.get("/api/predict-city/{city}")
async def predict_city(city: str, limit: int = 5000):
    """Predict era for unlabeled buildings in a city (reads predict.parquet)."""
    try:
        import pandas as pd
        from pathlib import Path
        from predict_era import predict_batch, ERA_LABELS

        predict_path = Path(r"D:\PROJELER\ml_data\predict.parquet")
        if not predict_path.exists():
            raise HTTPException(404, "predict.parquet not found — run feature_engineering.py")

        df = pd.read_parquet(predict_path)
        city_df = df[df["city"] == city].head(limit)
        if len(city_df) == 0:
            raise HTTPException(404, f"No unlabeled buildings for city: {city}")

        # NaN → None for JSON serialization
        city_df = city_df.where(city_df.notna(), other=None)
        buildings = city_df.to_dict("records")
        results = predict_batch(buildings, city)

        era_counts = {}
        for r in results:
            era_name = r["predicted_era_name"]
            era_counts[era_name] = era_counts.get(era_name, 0) + 1

        # Strip non-serializable fields (geometry, raw floats) from response
        slim = [{k: v for k, v in r.items()
                 if k in ("lon","lat","height","predicted_era","predicted_era_name","predicted_era_color","confidence")}
                for r in results]

        return {
            "city": city,
            "count": len(results),
            "era_distribution": era_counts,
            "buildings": slim[:100],  # cap response size; full data in parquet
        }
    except FileNotFoundError:
        raise HTTPException(503, "Model not loaded — run train_model.py first")
    except Exception as e:
        raise HTTPException(500, str(e))


class ConnectionManager:
    """Aktif WebSocket bağlantılarını tutar, ephemeral broadcast yapar."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict, exclude: WebSocket | None = None) -> None:
        for conn in list(self.active):
            if conn is exclude:
                continue
            try:
                await conn.send_json(message)
            except Exception:
                self.disconnect(conn)


manager = ConnectionManager()


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            # SPRINT 7: SoundNotePin payload {lat, lon, audio} broadcast edilir
            await manager.broadcast(data, exclude=ws)
    except WebSocketDisconnect:
        manager.disconnect(ws)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
