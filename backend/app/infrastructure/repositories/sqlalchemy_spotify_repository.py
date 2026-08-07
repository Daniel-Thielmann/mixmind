from __future__ import annotations

import time

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.domain.entities.spotify_connection import SpotifyConnection
from app.domain.repositories.spotify_connection_repository import (
    SpotifyConnectionRepository,
)
from app.infrastructure.database.mappers.spotify_connection_mapper import (
    SpotifyConnectionMapper,
)
from app.infrastructure.database.models.oauth_state_model import OAuthStateModel
from app.infrastructure.database.models.spotify_connection_model import (
    SpotifyConnectionModel,
)


class SqlAlchemySpotifyConnectionRepository(SpotifyConnectionRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_by_user_id(self, user_id: str) -> SpotifyConnection | None:
        model = (
            self._db.query(SpotifyConnectionModel)
            .filter(SpotifyConnectionModel.user_id == user_id)
            .first()
        )
        return SpotifyConnectionMapper.to_domain(model) if model else None

    def find_by_spotify_user_id(self, spotify_user_id: str) -> SpotifyConnection | None:
        model = (
            self._db.query(SpotifyConnectionModel)
            .filter(SpotifyConnectionModel.spotify_user_id == spotify_user_id)
            .first()
        )
        return SpotifyConnectionMapper.to_domain(model) if model else None

    def save(self, connection: SpotifyConnection) -> SpotifyConnection:
        existing_for_user = (
            self._db.query(SpotifyConnectionModel)
            .filter(SpotifyConnectionModel.user_id == connection.user_id)
            .first()
        )
        existing_for_spotify = (
            self._db.query(SpotifyConnectionModel)
            .filter(
                SpotifyConnectionModel.spotify_user_id == connection.spotify_user_id
            )
            .first()
        )

        # A successful Spotify OAuth callback proves control of the Spotify
        # account. If the MixMind identity changed (for example, Google to
        # GitHub login), transfer the existing connection instead of violating
        # the unique spotify_user_id constraint.
        existing: SpotifyConnectionModel | None
        if existing_for_spotify and (
            not existing_for_user or existing_for_spotify.id != existing_for_user.id
        ):
            if existing_for_user:
                self._db.delete(existing_for_user)
                self._db.flush()
            existing_for_spotify.user_id = connection.user_id
            existing = existing_for_spotify
        else:
            existing = existing_for_user

        if existing:
            existing.spotify_user_id = connection.spotify_user_id
            existing.spotify_display_name = connection.spotify_display_name
            existing.spotify_email = connection.spotify_email
            existing.access_token = connection.access_token
            existing.refresh_token = connection.refresh_token
            existing.token_type = connection.token_type
            existing.scope = connection.scope
            existing.expires_at = connection.expires_at
            existing.status = connection.status
            if connection.authorized_at:
                existing.authorized_at = connection.authorized_at
            if connection.last_refresh_at:
                existing.last_refresh_at = connection.last_refresh_at
            self._db.flush()
            return SpotifyConnectionMapper.to_domain(existing)

        model = SpotifyConnectionMapper.to_persistence(connection)
        self._db.add(model)
        self._db.flush()
        return SpotifyConnectionMapper.to_domain(model)

    def delete_by_user_id(self, user_id: str) -> None:
        self._db.query(SpotifyConnectionModel).filter(
            SpotifyConnectionModel.user_id == user_id
        ).delete()
        self._db.flush()

    def mark_reauthorization_required(self, user_id: str) -> None:
        stmt = (
            update(SpotifyConnectionModel)
            .where(SpotifyConnectionModel.user_id == user_id)
            .values(
                status="reauthorization_required",
                access_token="",
                refresh_token="",
            )
        )
        self._db.execute(stmt)
        self._db.flush()

    # --- OAuth State ---

    def create_oauth_state(
        self, nonce: str, user_id: str, provider: str, expires_at: int
    ) -> None:
        model = OAuthStateModel(
            nonce=nonce,
            user_id=user_id,
            provider=provider,
            expires_at=expires_at,
            consumed=False,
        )
        self._db.add(model)
        self._db.flush()

    def find_oauth_state(self, nonce: str) -> OAuthStateModel | None:
        return (
            self._db.query(OAuthStateModel)
            .filter(OAuthStateModel.nonce == nonce)
            .first()
        )

    def consume_oauth_state(self, nonce: str) -> bool:
        now = int(time.time())
        result = (
            self._db.query(OAuthStateModel)
            .filter(
                OAuthStateModel.nonce == nonce,
                OAuthStateModel.consumed == False,  # noqa: E712 — SQLAlchemy 2.0 raises TypeError on `not column`
                OAuthStateModel.expires_at > now,
            )
            .update({"consumed": True})
        )
        self._db.flush()
        return result > 0

    def delete_expired_oauth_states(self) -> None:
        now = int(time.time())
        self._db.query(OAuthStateModel).filter(
            OAuthStateModel.expires_at <= now
        ).delete()
        self._db.flush()
