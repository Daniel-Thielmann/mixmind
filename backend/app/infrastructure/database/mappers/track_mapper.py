"""Maps TrackEntity (Domain) ⇄ TrackModel (ORM)."""

from __future__ import annotations

import uuid

from app.domain.entities.track import Track
from app.domain.value_objects.bpm import BPM
from app.domain.value_objects.camelot_key import CamelotKey
from app.domain.value_objects.duration import Duration
from app.domain.value_objects.energy import Energy
from app.domain.value_objects.identifiers import TrackId
from app.infrastructure.database.models.track_model import TrackModel


class TrackMapper:
    @staticmethod
    def to_persistence(entity: Track) -> TrackModel:
        return TrackModel(
            id=uuid.UUID(hex=entity.track_id.value),
            filename=entity.filename,
            duration=entity.duration.value if entity.duration else None,
            bpm=entity.bpm.value if entity.bpm else None,
            energy=entity.energy.value if entity.energy else None,
            key=entity.key,
            camelot=entity.camelot.value if entity.camelot else None,
            sample_rate=entity.sample_rate,
        )

    @staticmethod
    def to_domain(model: TrackModel) -> Track:
        return Track(
            track_id=TrackId(value=model.id.hex),
            filename=model.filename,
            duration=Duration(value=model.duration)
            if model.duration is not None
            else None,
            bpm=BPM(value=model.bpm) if model.bpm is not None else None,
            energy=Energy(value=model.energy) if model.energy is not None else None,
            key=model.key,
            camelot=CamelotKey(value=model.camelot)
            if model.camelot is not None
            else None,
            sample_rate=model.sample_rate,
        )
