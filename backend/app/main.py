from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(
    title="MixMind AI API",
    description="""
AI-powered assistant for DJs capable of analyzing electronic music tracks
using Digital Signal Processing (DSP) and Music Information Retrieval (MIR).
""",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def health_check():
    return {"project": "MixMind AI", "status": "running", "version": "0.1.0"}
