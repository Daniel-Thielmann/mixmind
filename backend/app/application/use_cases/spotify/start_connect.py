from __future__ import annotations

import logging

from app.application.dto.spotify import SpotifyAuthorizeUrlResponse
from app.application.use_cases.spotify.state_service import SpotifyStateService
from app.domain.repositories.spotify_connection_repository import (
    SpotifyConnectionRepository,
)
from app.infrastructure.spotify.oauth_client import SpotifyOAuthClient

logger = logging.getLogger(__name__)


class StartSpotifyConnectUseCase:
    def __init__(
        self,
        oauth_client: SpotifyOAuthClient | None = None,
        state_service: SpotifyStateService | None = None,
        repository: SpotifyConnectionRepository | None = None,
    ) -> None:
        self._oauth = oauth_client or SpotifyOAuthClient()
        self._state_service = state_service or SpotifyStateService()
        if repository:
            self._state_service.set_repository(repository)

    def execute(
        self, user_id: str, return_to: str = "/dashboard"
    ) -> SpotifyAuthorizeUrlResponse:
        logger.info("Starting Spotify connection for user %s", user_id)
        state = self._state_service.create_state(user_id, return_to)
        url = self._oauth.build_authorize_url(state)
        return SpotifyAuthorizeUrlResponse(authorization_url=url)
