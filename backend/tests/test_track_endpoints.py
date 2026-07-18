from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_track_repository
from app.domain.entities.track import AudioAnalysis, Track
from app.domain.repositories.track_repository import TrackRepository
from app.domain.value_objects.identifiers import TrackId
from app.main import app


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

    def get_audio_path(self, filename: str) -> Path | None:
        return None


def test_tracks_crud_endpoints() -> None:
    repository = InMemoryTrackRepository()
    app.dependency_overrides[get_track_repository] = lambda: repository
    client = TestClient(app)
    try:
        created = client.post(
            "/api/v1/tracks",
            json={"filename": "track.mp3", "bpm": 128, "energy": 0.8},
        )
        assert created.status_code == 201
        track_id = created.json()["id"]

        fetched = client.get(f"/api/v1/tracks/{track_id}")
        assert fetched.status_code == 200
        assert fetched.json()["filename"] == "track.mp3"

        listed = client.get("/api/v1/tracks")
        assert listed.status_code == 200
        assert len(listed.json()) == 1

        updated = client.patch(
            f"/api/v1/tracks/{track_id}", json={"filename": "updated.mp3"}
        )
        assert updated.status_code == 200
        assert updated.json()["filename"] == "updated.mp3"

        deleted = client.delete(f"/api/v1/tracks/{track_id}")
        assert deleted.status_code == 204
        assert client.get(f"/api/v1/tracks/{track_id}").status_code == 404
    finally:
        app.dependency_overrides.clear()
