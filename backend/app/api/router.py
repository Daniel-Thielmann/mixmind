from __future__ import annotations

from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.core.config import settings
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

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
