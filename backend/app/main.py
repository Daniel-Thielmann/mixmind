from fastapi import FastAPI
from app.core.config import settings
from app.api.router import api_router
from contextlib import asynccontextmanager
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check():
    return {"project": "MixMind AI", "status": "running", "version": "0.1.0"}
