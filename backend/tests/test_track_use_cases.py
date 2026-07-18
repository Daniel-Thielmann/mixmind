import pytest

from app.application.use_cases.track.create.use_case import CreateTrackUseCase
from app.application.use_cases.track.delete.use_case import DeleteTrackUseCase
from app.application.use_cases.track.dto import CreateTrackRequest, UpdateTrackRequest
from app.application.use_cases.track.get.use_case import GetTrackUseCase
from app.application.use_cases.track.list.use_case import ListTracksUseCase
from app.application.use_cases.track.update.use_case import UpdateTrackUseCase
from app.core.exceptions import NotFoundError
from app.domain.entities.track import AudioAnalysis, Track
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.identifiers import TrackId


class InMemoryTrackRepository(TrackRepository):
    def __init__(self) -> None:
        self.tracks: dict[str, Track] = {}

    def save(self, entity: Track) -> None:
        self.tracks[entity.track_id.value] = entity

    def find_by_id(self, track_id: TrackId) -> Track | None:
        return self.tracks.get(track_id.value)

    def find_all(self) -> list[Track]:
        return list(self.tracks.values())

    def update(self, entity: Track) -> None:
        self.save(entity)

    def delete(self, track_id: TrackId) -> None:
        self.tracks.pop(track_id.value, None)

    def save_analysis(self, analysis_id: str, analysis: AudioAnalysis) -> None:
        raise NotImplementedError

    def get_analysis(self, analysis_id: str) -> AudioAnalysis | None:
        return None

    def get_audio_path(self, filename: str):
        return None


def test_track_crud_use_cases() -> None:
    repository = InMemoryTrackRepository()
    created = CreateTrackUseCase(repository).execute(
        CreateTrackRequest(filename="track.mp3", bpm=128, energy=0.8)
    )

    fetched = GetTrackUseCase(repository).execute(TrackId(created.id))
    assert fetched.filename == "track.mp3"
    assert len(ListTracksUseCase(repository).execute()) == 1

    updated = UpdateTrackUseCase(repository).execute(
        TrackId(created.id), UpdateTrackRequest(filename="updated.mp3", bpm=130)
    )
    assert updated.filename == "updated.mp3"
    assert updated.bpm == 130

    DeleteTrackUseCase(repository).execute(TrackId(created.id))
    assert ListTracksUseCase(repository).execute() == []


def test_get_missing_track_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        GetTrackUseCase(InMemoryTrackRepository()).execute(TrackId())
