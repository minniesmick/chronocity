"""ChronoCity backend — FastAPI.

Scaffold (SPRINT 0):
- GET  /api/health   → health check
- WS   /ws           → ephemeral broadcast (ses notları, SoundNotePin — SPRINT 7)

Veri persist edilmez (brief: WebSocket ephemeral). Ses notları bellekte tutulan
bağlantılara yayınlanır, kayıt yok.
"""
from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="ChronoCity API", version="0.1.0")

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
