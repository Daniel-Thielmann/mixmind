"""Fixtures for integration tests — real PostgreSQL, per-test transaction rollback."""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.base import Base
from app.infrastructure.database.config import database_settings

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    database_settings.database_url,
)


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session_local = sessionmaker(bind=connection)
    session = session_local()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def repository(session):
    from app.infrastructure.repositories import SqlAlchemyTrackRepository

    return SqlAlchemyTrackRepository(session=session)
