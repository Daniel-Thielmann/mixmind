from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from app.api.router import api_router
from app.core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    settings.processed_path.mkdir(parents=True, exist_ok=True)
    settings.temp_path.mkdir(parents=True, exist_ok=True)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
AI-powered assistant for DJs capable of analyzing electronic music tracks
using Digital Signal Processing (DSP) and Music Information Retrieval (MIR).
""",
    lifespan=lifespan,
)

# =====================================================================
# CORS
# =====================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# Static Files
# =====================================================================

app.mount(
    "/processed",
    StaticFiles(directory=settings.processed_path),
    name="processed",
)

# =====================================================================
# API
# =====================================================================

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {
        "project": "MixMind AI",
        "status": "running",
        "version": settings.APP_VERSION,
    }
