from __future__ import annotations

from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Persistent Cognitive Infrastructure Control Plane",
        version="0.1.0",
        docs_url="/docs" if settings.enable_openapi else None,
        redoc_url="/redoc" if settings.enable_openapi else None,
    )
    app.include_router(router)
    FastAPIInstrumentor.instrument_app(app)
    return app


app = create_app()

