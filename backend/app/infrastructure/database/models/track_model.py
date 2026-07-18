"""SQLAlchemy ORM model for track persistence."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class TrackModel(Base):
    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String(255))
    duration: Mapped[float | None] = mapped_column(Float)
    bpm: Mapped[float | None] = mapped_column(Float)
    energy: Mapped[float | None] = mapped_column(Float)
    key: Mapped[str] = mapped_column(String(50))
    camelot: Mapped[str | None] = mapped_column(String(10))
    sample_rate: Mapped[int] = mapped_column(Integer)
