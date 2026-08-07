from __future__ import annotations

import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.domain.entities.spotify_connection import SpotifyConnection
from app.infrastructure.database.base import Base
from app.infrastructure.database.models.spotify_connection_model import (
    SpotifyConnectionModel,
)
from app.infrastructure.repositories.sqlalchemy_spotify_repository import (
    SqlAlchemySpotifyConnectionRepository,
)


def _connection(user_id: str, spotify_user_id: str, token: str) -> SpotifyConnection:
    return SpotifyConnection(
        user_id=user_id,
        spotify_user_id=spotify_user_id,
        access_token=token,
        refresh_token=f"refresh-{token}",
        expires_at=int(time.time()) + 3600,
    )


def test_save_transfers_spotify_account_to_new_mixmind_user() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[SpotifyConnectionModel.__table__])

    with Session(engine) as session:
        repository = SqlAlchemySpotifyConnectionRepository(session)
        original = repository.save(_connection("google-user", "spotify-1", "old"))
        transferred = repository.save(_connection("github-user", "spotify-1", "new"))

        assert transferred.id == original.id
        assert transferred.user_id == "github-user"
        assert transferred.access_token == "new"
        assert repository.find_by_user_id("google-user") is None
        assert repository.find_by_user_id("github-user") is not None


def test_transfer_replaces_current_users_previous_spotify_connection() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[SpotifyConnectionModel.__table__])

    with Session(engine) as session:
        repository = SqlAlchemySpotifyConnectionRepository(session)
        repository.save(_connection("old-owner", "spotify-1", "old"))
        repository.save(_connection("new-owner", "spotify-2", "other"))

        transferred = repository.save(
            _connection("new-owner", "spotify-1", "replacement")
        )

        rows = session.query(SpotifyConnectionModel).all()
        assert len(rows) == 1
        assert transferred.user_id == "new-owner"
        assert transferred.spotify_user_id == "spotify-1"
        assert transferred.access_token == "replacement"
