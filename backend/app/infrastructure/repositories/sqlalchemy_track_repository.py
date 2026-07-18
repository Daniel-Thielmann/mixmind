"""SQLAlchemy implementation of TrackRepository."""

from __future__ import annotations

import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.domain.entities.track import AudioAnalysis, Track
from app.domain.repositories import TrackRepository
from app.domain.value_objects.identifiers import TrackId
from app.infrastructure.database.mappers import TrackMapper
from app.infrastructure.database.models import TrackModel


class SqlAlchemyTrackRepository(TrackRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, entity: Track) -> None:
        model = TrackMapper.to_persistence(entity)
        self._session.add(model)

    def find_by_id(self, track_id: TrackId) -> Track | None:
        model = self._session.get(TrackModel, uuid.UUID(hex=track_id.value))
        return TrackMapper.to_domain(model) if model else None

    def find_all(self) -> list[Track]:
        models = self._session.query(TrackModel).all()
        return [TrackMapper.to_domain(m) for m in models]

    def update(self, entity: Track) -> None:
        model = TrackMapper.to_persistence(entity)
        self._session.merge(model)

    def delete(self, track_id: TrackId) -> None:
        model = self._session.get(TrackModel, uuid.UUID(hex=track_id.value))
        if model:
            self._session.delete(model)

    def save_analysis(self, analysis_id: str, analysis: AudioAnalysis) -> None:
        model = self._session.get(TrackModel, uuid.UUID(hex=analysis_id))
        if model:
            model.filename = analysis.filename
            model.duration = analysis.duration
            model.bpm = analysis.bpm
            model.energy = analysis.energy
            model.key = analysis.key
            model.camelot = analysis.camelot
            model.sample_rate = analysis.sample_rate
        else:
            model = TrackModel(
                id=uuid.UUID(hex=analysis_id),
                filename=analysis.filename,
                duration=analysis.duration,
                bpm=analysis.bpm,
                energy=analysis.energy,
                key=analysis.key,
                camelot=analysis.camelot,
                sample_rate=analysis.sample_rate,
            )
            self._session.add(model)

    def get_analysis(self, analysis_id: str) -> AudioAnalysis | None:
        model = self._session.get(TrackModel, uuid.UUID(hex=analysis_id))
        if model is None:
            return None
        return AudioAnalysis(
            filename=model.filename,
            duration=model.duration if model.duration is not None else 0.0,
            sample_rate=model.sample_rate,
            bpm=model.bpm if model.bpm is not None else 0.0,
            energy=model.energy if model.energy is not None else 0.0,
            key=model.key,
            camelot=model.camelot if model.camelot is not None else "Unknown",
        )

    def get_audio_path(self, filename: str) -> Path | None:
        path = Path(f"uploads/{filename}")
        return path if path.exists() else None
