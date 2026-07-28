from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import ClassVar

from app.domain.entities.spotify_connection import SpotifyConnection
from app.domain.repositories.spotify_connection_repository import (
    SpotifyConnectionRepository,
)
from app.infrastructure.spotify.oauth_client import (
    SpotifyGrantError,
    SpotifyOAuthClient,
)

logger = logging.getLogger(__name__)


class RefreshSpotifyAccessTokenUseCase:
    _refresh_locks: ClassVar[dict[str, asyncio.Lock]] = {}

    def __init__(
        self,
        oauth_client: SpotifyOAuthClient | None = None,
        repository: SpotifyConnectionRepository | None = None,
    ) -> None:
        self._oauth = oauth_client or SpotifyOAuthClient()
        self._repository = repository

    def set_repository(self, repository: SpotifyConnectionRepository) -> None:
        self._repository = repository

    @classmethod
    def _get_user_lock(cls, user_id: str) -> asyncio.Lock:
        if user_id not in cls._refresh_locks:
            cls._refresh_locks[user_id] = asyncio.Lock()
        return cls._refresh_locks[user_id]

    async def execute(self, user_id: str) -> SpotifyConnection | None:
        if not self._repository:
            return None

        async with self._get_user_lock(user_id):
            return await self._execute_refresh(user_id)

    async def _execute_refresh(self, user_id: str) -> SpotifyConnection | None:
        connection = self._repository.find_by_user_id(user_id)
        if not connection:
            return None

        if not connection.is_expired:
            return connection

        if connection.needs_reauthorization:
            logger.info("User %s needs reauthorization for Spotify", user_id)
            return None

        if not connection.refresh_token:
            logger.warning("No refresh token available for user %s", user_id)
            self._repository.mark_reauthorization_required(user_id)
            return None

        try:
            token_response = await self._oauth.refresh_access_token(
                connection.refresh_token
            )
        except SpotifyGrantError as exc:
            if exc.error == "invalid_grant":
                logger.warning(
                    "Spotify refresh token expired or revoked for user %s", user_id
                )
                self._repository.mark_reauthorization_required(user_id)
                return None
            logger.error(
                "Spotify token refresh grant error for user %s: %s", user_id, exc.error
            )
            return None
        except Exception:
            logger.error("Failed to refresh Spotify token for user %s", user_id)
            return None

        connection.access_token = token_response.access_token
        connection.expires_at = int(time.time()) + token_response.expires_in
        connection.last_refresh_at = datetime.now(UTC).replace(tzinfo=None)
        if token_response.refresh_token:
            connection.refresh_token = token_response.refresh_token

        connection = self._repository.save(connection)
        logger.info("Refreshed Spotify token for user %s", user_id)
        return connection
