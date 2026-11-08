from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_schema, is_empty, scalar
from .seed import seed
from .service import dashboard

DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def ensure_data() -> None:
    init_schema()
    seed_if_empty()


def seed_if_empty() -> None:
    if is_empty():
        seed()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_data()
    yield


app = FastAPI(title="CRM Funnel API", version="1.0.0", lifespan=lifespan)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "leads": int(scalar("SELECT COUNT(*) FROM leads"))}


@app.get("/api/dashboard")
def get_dashboard() -> dict:
    return dashboard()


if DIST.exists():
    app.mount("/", StaticFiles(directory=DIST, html=True), name="ui")
else:
    @app.get("/", response_class=HTMLResponse)
    def placeholder() -> str:
        return "<h1>CRM Funnel API</h1><p>Соберите фронтенд: npm run build</p>"
