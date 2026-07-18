from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.domain.repositories.track_repository import TrackRepository
from app.infrastructure.database.session import get_db
from app.infrastructure.repositories.sqlalchemy_track_repository import (
    SqlAlchemyTrackRepository,
)

DatabaseSession = Annotated[Session, Depends(get_db)]


def get_track_repository(db: DatabaseSession) -> TrackRepository:
    return SqlAlchemyTrackRepository(db)


TrackRepositoryDependency = Annotated[TrackRepository, Depends(get_track_repository)]
