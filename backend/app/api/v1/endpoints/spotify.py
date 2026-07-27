from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import DatabaseSession, get_current_owner_id
from app.application.dto.spotify import (
    SpotifyAuthorizeUrlResponse,
    SpotifyConnectionStatusResponse,
)
from app.application.use_cases.spotify.complete_connect import (
    CompleteSpotifyConnectionUseCase,
)
from app.application.use_cases.spotify.disconnect import DisconnectSpotifyUseCase
from app.application.use_cases.spotify.get_status import (
    GetSpotifyConnectionStatusUseCase,
)
from app.application.use_cases.spotify.refresh_token import (
    RefreshSpotifyAccessTokenUseCase,
)
from app.application.use_cases.spotify.start_connect import (
    StartSpotifyConnectUseCase,
)
from app.core.config import settings
from app.core.exceptions import SpotifyAuthenticationError
from app.infrastructure.repositories.sqlalchemy_spotify_repository import (
    SqlAlchemySpotifyConnectionRepository,
)
from app.infrastructure.spotify.extended_api_client import (
    ExtendedSpotifyApiClient,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations/spotify", tags=["Integrations"])


def _get_repository(db: Session) -> SqlAlchemySpotifyConnectionRepository:
    return SqlAlchemySpotifyConnectionRepository(db)


def _get_spotify_client(db: Session, user_id: str) -> ExtendedSpotifyApiClient:
    repo = _get_repository(db)
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
        refreshed = refresher.execute(user_id)
        if not refreshed:
            raise SpotifyAuthenticationError(
                detail="Your Spotify session has expired. Please reconnect."
            )
        access_token = refreshed.access_token

    return ExtendedSpotifyApiClient(access_token=access_token)


@router.get("/status", response_model=SpotifyConnectionStatusResponse)
def get_status(
    db: DatabaseSession,
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyConnectionStatusResponse:
    use_case = GetSpotifyConnectionStatusUseCase(
        repository=_get_repository(db),
    )
    return use_case.execute(user_id)


@router.get("/connect", response_model=SpotifyAuthorizeUrlResponse)
def connect(
    db: DatabaseSession,
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyAuthorizeUrlResponse:
    use_case = StartSpotifyConnectUseCase(
        repository=_get_repository(db),
    )
    return use_case.execute(user_id)


@router.get("/callback")
def callback(
    db: DatabaseSession,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
) -> RedirectResponse:
    frontend_url = settings.FRONTEND_URL or "http://127.0.0.1:3000"
    redirect_to = f"{frontend_url}/dashboard/settings/integrations"

    if not state:
        return RedirectResponse(
            url=f"{redirect_to}?spotify=error&message=missing_state",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    use_case = CompleteSpotifyConnectionUseCase(
        repository=_get_repository(db),
    )
    connection, err_msg = use_case.execute(
        code=code,
        state=state,
        error=error,
    )

    if err_msg or not connection:
        from urllib.parse import quote

        return RedirectResponse(
            url=f"{redirect_to}?spotify=error&message={quote(err_msg or 'unknown')}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return RedirectResponse(
        url=f"{redirect_to}?spotify=connected",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def disconnect(
    db: DatabaseSession,
    user_id: str = Depends(get_current_owner_id),
) -> None:
    use_case = DisconnectSpotifyUseCase(
        repository=_get_repository(db),
    )
    use_case.execute(user_id)
    logger.info("Spotify disconnected for user %s", user_id)


class SpotifyTrackItemResponse(BaseModel):
    id: str
    name: str
    artists: list[dict]
    album: dict
    duration_ms: int
    external_urls: dict
    popularity: int


class SpotifyPagingResponse(BaseModel):
    href: str
    items: list[dict]
    limit: int
    next: str | None
    offset: int
    previous: str | None
    total: int


@router.get("/playlists")
async def get_spotify_playlists(
    db: DatabaseSession,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyPagingResponse:
    client = _get_spotify_client(db, user_id)
    paging = await client.get_user_playlists(limit=limit, offset=offset)
    return SpotifyPagingResponse(
        href=paging.href,
        items=paging.items,
        limit=paging.limit,
        next=paging.next,
        offset=paging.offset,
        previous=paging.previous,
        total=paging.total,
    )


@router.get("/playlists/{playlist_id}/tracks")
async def get_playlist_tracks(
    playlist_id: str,
    db: DatabaseSession,
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyPagingResponse:
    client = _get_spotify_client(db, user_id)
    paging = await client.get_playlist_tracks(
        playlist_id=playlist_id, limit=limit, offset=offset
    )
    return SpotifyPagingResponse(
        href=paging.href,
        items=paging.items,
        limit=paging.limit,
        next=paging.next,
        offset=paging.offset,
        previous=paging.previous,
        total=paging.total,
    )


@router.get("/saved-tracks")
async def get_saved_tracks(
    db: DatabaseSession,
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyPagingResponse:
    client = _get_spotify_client(db, user_id)
    paging = await client.get_saved_tracks(limit=limit, offset=offset)
    return SpotifyPagingResponse(
        href=paging.href,
        items=paging.items,
        limit=paging.limit,
        next=paging.next,
        offset=paging.offset,
        previous=paging.previous,
        total=paging.total,
    )


@router.get("/search")
async def search_spotify_tracks(
    db: DatabaseSession,
    q: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_owner_id),
) -> SpotifyPagingResponse:
    client = _get_spotify_client(db, user_id)
    paging = await client.search_tracks(query=q, limit=limit, offset=offset)
    return SpotifyPagingResponse(
        href=paging.href,
        items=paging.items,
        limit=paging.limit,
        next=paging.next,
        offset=paging.offset,
        previous=paging.previous,
        total=paging.total,
    )
