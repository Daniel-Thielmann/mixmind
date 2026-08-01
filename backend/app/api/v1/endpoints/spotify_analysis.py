from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import DatabaseSession, get_current_owner_id
from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.spotify_analysis.dto import (
    SpotifyAnalysisRequest,
)
from app.application.use_cases.analysis.spotify_analysis.service import (
    SpotifyAnalysisService,
    spotify_analysis_service,
)
from app.application.use_cases.spotify.refresh_token import (
    RefreshSpotifyAccessTokenUseCase,
)
from app.core.exceptions import (
    AppError,
    SpotifyAuthenticationError,
)
from app.infrastructure.repositories.sqlalchemy_spotify_repository import (
    SqlAlchemySpotifyConnectionRepository,
)
from app.infrastructure.spotify.extended_api_client import ExtendedSpotifyApiClient

logger = logging.getLogger(__name__)

router = APIRouter()
_analysis_slot = asyncio.Semaphore(1)


async def _get_spotify_client(db: Session, user_id: str) -> ExtendedSpotifyApiClient:
    repo = SqlAlchemySpotifyConnectionRepository(db)
    connection = repo.find_by_user_id(user_id)
    if not connection or connection.status == "disconnected":
        raise SpotifyAuthenticationError(
            detail="You need to connect your Spotify account first."
        )

    if connection.status == "reauthorization_required":
        raise SpotifyAuthenticationError(
            detail="Your Spotify session has expired. Please reconnect."
        )

    access_token = connection.access_token
    if connection.is_expired:
        refresher = RefreshSpotifyAccessTokenUseCase(repository=repo)
        refreshed = await refresher.execute(user_id)
        if not refreshed:
            raise SpotifyAuthenticationError(
                detail="Your Spotify session has expired. Please reconnect."
            )
        access_token = refreshed.access_token

    async def refresh_after_unauthorized() -> str | None:
        refreshed = await RefreshSpotifyAccessTokenUseCase(repository=repo).execute(
            user_id
        )
        return refreshed.access_token if refreshed else None

    return ExtendedSpotifyApiClient(
        access_token=access_token,
        refresh_access_token=refresh_after_unauthorized,
    )


@router.post(
    "/spotify",
    response_model=UploadAnalysisResponse,
    summary="Analyze two tracks selected from Spotify",
)
async def analyze_spotify_tracks(
    request: SpotifyAnalysisRequest,
    db: DatabaseSession,
    user_id: str = Depends(get_current_owner_id),
    service: SpotifyAnalysisService = Depends(lambda: spotify_analysis_service),
) -> UploadAnalysisResponse:
    if _analysis_slot.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another analysis is already running. Please try again shortly.",
        )

    spotify_client = await _get_spotify_client(db, user_id)

    async with _analysis_slot:
        try:
            response = await service.analyze(
                request,
                spotify_client,
            )
        except AppError:
            raise
        except Exception as exc:
            logger.exception("Spotify analysis failed unexpectedly")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred during Spotify analysis.",
            ) from exc

    return response
