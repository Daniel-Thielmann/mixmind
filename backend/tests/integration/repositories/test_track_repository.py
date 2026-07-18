"""Integration tests for SqlAlchemyTrackRepository against a real PostgreSQL."""

from __future__ import annotations

from app.domain.entities.track import AudioAnalysis, Track
from app.domain.value_objects.bpm import BPM
from app.domain.value_objects.camelot_key import CamelotKey
from app.domain.value_objects.duration import Duration
from app.domain.value_objects.energy import Energy
from app.domain.value_objects.identifiers import TrackId


class TestSaveAndFindById:
    def test_save_and_find_by_id(self, repository, session):
        track_id = TrackId(value="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")
        track = Track(
            track_id=track_id,
            filename="track.wav",
            duration=Duration(value=180.0),
            bpm=BPM(value=128.0),
            energy=Energy(value=0.75),
            key="C Minor",
            camelot=CamelotKey(value="1A"),
            sample_rate=44100,
        )
        repository.save(track)
        session.flush()

        found = repository.find_by_id(track_id)

        assert found is not None
        assert found.track_id == track.track_id
        assert found.filename == "track.wav"
        assert found.duration == Duration(value=180.0)
        assert found.bpm == BPM(value=128.0)
        assert found.energy == Energy(value=0.75)
        assert found.key == "C Minor"
        assert found.camelot == CamelotKey(value="1A")
        assert found.sample_rate == 44100

    def test_find_by_id_returns_none_when_missing(self, repository):
        track_id = TrackId(value="00000000000000000000000000000000")
        assert repository.find_by_id(track_id) is None


class TestFindAll:
    def test_find_all_returns_all_tracks(self, repository, session):
        track_1 = Track(
            track_id=TrackId(value="11111111111111111111111111111111"),
            filename="alpha.wav",
        )
        track_2 = Track(
            track_id=TrackId(value="22222222222222222222222222222222"),
            filename="beta.wav",
        )
        repository.save(track_1)
        repository.save(track_2)
        session.flush()

        results = repository.find_all()

        assert len(results) == 2
        ids = {str(t.track_id) for t in results}
        assert ids == {
            "11111111111111111111111111111111",
            "22222222222222222222222222222222",
        }

    def test_find_all_empty_when_no_tracks(self, repository):
        assert repository.find_all() == []


class TestUpdate:
    def test_update_existing_track(self, repository, session):
        track_id = TrackId(value="33333333333333333333333333333333")
        track = Track(
            track_id=track_id,
            filename="original.wav",
            duration=Duration(value=120.0),
        )
        repository.save(track)
        session.flush()

        track.filename = "updated.wav"
        track.duration = Duration(value=240.0)
        repository.update(track)
        session.flush()

        found = repository.find_by_id(track_id)
        assert found is not None
        assert found.filename == "updated.wav"
        assert found.duration == Duration(value=240.0)


class TestDelete:
    def test_delete_removes_track(self, repository, session):
        track_id = TrackId(value="44444444444444444444444444444444")
        track = Track(track_id=track_id, filename="to_delete.wav")
        repository.save(track)
        session.flush()

        repository.delete(track_id)
        session.flush()

        assert repository.find_by_id(track_id) is None

    def test_delete_nonexistent_track_does_not_raise(self, repository):
        track_id = TrackId(value="55555555555555555555555555555555")
        repository.delete(track_id)


class TestSaveAndGetAnalysis:
    def test_save_and_get_analysis(self, repository, session):
        analysis_id = "66666666666666666666666666666666"
        analysis = AudioAnalysis(
            filename="analysis_track.wav",
            duration=200.0,
            sample_rate=48000,
            bpm=140.0,
            energy=0.85,
            key="A Minor",
            camelot="8A",
        )
        repository.save_analysis(analysis_id, analysis)
        session.flush()

        found = repository.get_analysis(analysis_id)

        assert found is not None
        assert found.filename == "analysis_track.wav"
        assert found.duration == 200.0
        assert found.sample_rate == 48000
        assert found.bpm == 140.0
        assert found.energy == 0.85
        assert found.key == "A Minor"
        assert found.camelot == "8A"

    def test_get_analysis_returns_none_when_missing(self, repository):
        assert repository.get_analysis("00000000000000000000000000000000") is None


class TestGetAudioPath:
    def test_get_audio_path_returns_none_for_missing_file(self, repository):
        assert repository.get_audio_path("nonexistent.wav") is None
