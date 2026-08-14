from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.demo import router as demo_router
from app.api.v1.endpoints.spotify import router as spotify_router
from app.api.v1.endpoints.spotify_analysis import router as spotify_analysis_router
from app.api.v1.endpoints.storage import router as storage_router
from app.api.v1.endpoints.tracks import router as tracks_router
from app.api.v1.endpoints.youtube import router as youtube_router
from app.core.config import settings

api_router = APIRouter()


@api_router.get(
    "/health",
    tags=["Health"],
    summary="Global health check",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        },
    )


api_router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_router.include_router(demo_router, prefix="/demo", tags=["Demonstration"])
api_router.include_router(
    spotify_router, prefix="/integrations/spotify", tags=["Integrations"]
)
api_router.include_router(
    spotify_analysis_router, prefix="/analysis", tags=["Analysis"]
)
api_router.include_router(storage_router, prefix="/storage", tags=["Storage"])
api_router.include_router(tracks_router, prefix="/tracks", tags=["Tracks"])
api_router.include_router(youtube_router, prefix="/youtube", tags=["YouTube"])
