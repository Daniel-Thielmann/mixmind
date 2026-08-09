from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.application.use_cases.analysis.spotify_analysis.dto import (
    SpotifyAnalysisRequest,
    SpotifyTrackRequest,
)
from app.application.use_cases.analysis.spotify_analysis.service import (
    SpotifyAnalysisService,
)
from app.core.exceptions import (
    AudioDownloadNotFoundError,
    AudioDurationMismatchError,
    AudioProviderUnavailableError,
    InvalidDownloadedAudioError,
)
from app.domain.value_objects.acquired_audio import AcquiredAudio
from app.domain.value_objects.spotify_track import SpotifyTrackMetadata

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "rapidapi"


class TestSpotifyAnalysisRequest:
    def test_valid_request_succeeds(self) -> None:
        request = SpotifyAnalysisRequest(
            tracks=[
                SpotifyTrackRequest(position="track_a", spotify_track_id="id1"),
                SpotifyTrackRequest(position="track_b", spotify_track_id="id2"),
            ]
        )
        assert len(request.tracks) == 2
        assert request.get_track_a().spotify_track_id == "id1"
        assert request.get_track_b().spotify_track_id == "id2"

    def test_fails_with_same_ids(self) -> None:
        with pytest.raises(ValidationError, match="must be different"):
            SpotifyAnalysisRequest(
                tracks=[
                    SpotifyTrackRequest(position="track_a", spotify_track_id="same"),
                    SpotifyTrackRequest(position="track_b", spotify_track_id="same"),
                ]
            )

    def test_fails_without_track_b(self) -> None:
        with pytest.raises(ValidationError):
            SpotifyAnalysisRequest(
                tracks=[
                    SpotifyTrackRequest(position="track_a", spotify_track_id="id1"),
                ]
            )

    def test_fails_with_two_track_a(self) -> None:
        with pytest.raises(ValidationError, match="Must include exactly one"):
            SpotifyAnalysisRequest(
                tracks=[
                    SpotifyTrackRequest(position="track_a", spotify_track_id="id1"),
                    SpotifyTrackRequest(position="track_a", spotify_track_id="id2"),
                ]
            )

    def test_fails_with_empty_id(self) -> None:
        with pytest.raises(ValidationError):
            SpotifyAnalysisRequest(
                tracks=[
                    SpotifyTrackRequest(position="track_a", spotify_track_id=""),
                    SpotifyTrackRequest(position="track_b", spotify_track_id="id2"),
                ]
            )


class TestSpotifyTrackMetadata:
    def test_basic_creation(self) -> None:
        meta = SpotifyTrackMetadata(
            spotify_id="abc123",
            spotify_url="https://open.spotify.com/track/abc123",
            title="Test Track",
            artists=("Artist A", "Artist B"),
            album="Test Album",
            duration_ms=240000,
        )
        assert meta.duration_seconds == 240.0
        assert meta.artist_names == "Artist A, Artist B"
        assert "abc123" in meta.filename_safe()
        assert "Test Track" in meta.filename_safe()

    def test_filename_sanitization(self) -> None:
        meta = SpotifyTrackMetadata(
            spotify_id="xyz",
            spotify_url="https://open.spotify.com/track/xyz",
            title="Song/With:Special*Chars?",
            artists=("Artist",),
            album="Album",
            duration_ms=180000,
        )
        safe = meta.filename_safe()
        assert "/" not in safe
        assert ":" not in safe
        assert "?" not in safe
        assert safe.endswith(".mp3")


class TestSpotifyConfig:
    def test_defaults_are_empty_when_not_set(self) -> None:
        from app.core.config import Settings

        s = Settings(
            _env_file=None,
            _env_file_encoding=None,
        )
        assert s.RAPIDAPI_KEY == ""
        assert s.RAPIDAPI_SPOTIFY_DOWNLOADER_HOST == ""
        assert s.RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL == ""

    def test_rapidapi_vars_loaded_from_env(self) -> None:
        import os

        os.environ.setdefault("RAPIDAPI_KEY", "test_key_123")
        os.environ.setdefault(
            "RAPIDAPI_SPOTIFY_DOWNLOADER_HOST", "test-host.p.rapidapi.com"
        )
        os.environ.setdefault(
            "RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL", "https://test-host.p.rapidapi.com"
        )
        from app.core.config import Settings

        s = Settings()
        assert s.RAPIDAPI_KEY == "test_key_123"
        assert s.RAPIDAPI_SPOTIFY_DOWNLOADER_HOST == "test-host.p.rapidapi.com"
        assert (
            s.RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL == "https://test-host.p.rapidapi.com"
        )


class TestRapidApiDownloader:
    @pytest.fixture(autouse=True)
    def _clear_rapidapi_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            settings as rd_settings,
        )

        monkeypatch.setattr(rd_settings, "RAPIDAPI_KEY", "")
        monkeypatch.setattr(rd_settings, "RAPIDAPI_SPOTIFY_DOWNLOADER_HOST", "")
        monkeypatch.setattr(rd_settings, "RAPIDAPI_SPOTIFY_DOWNLOADER_BASE_URL", "")
        monkeypatch.setattr(rd_settings, "RAPIDAPI_DOWNLOAD_TIMEOUT", 30)
        monkeypatch.setattr(rd_settings, "RAPIDAPI_REQUEST_TIMEOUT", 15)
        monkeypatch.setattr(rd_settings, "RAPIDAPI_DOWNLOAD_MAX_SIZE", 200)

    @pytest.fixture
    def track_meta(self) -> SpotifyTrackMetadata:
        return SpotifyTrackMetadata(
            spotify_id="abc123",
            spotify_url="https://open.spotify.com/track/abc123",
            title="Test Track",
            artists=("Artist",),
            album="Album",
            duration_ms=240000,
        )

    def test_missing_config_raises_error(
        self, track_meta: SpotifyTrackMetadata
    ) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            temp_dir=Path("/tmp"),
        )
        with pytest.raises(AudioProviderUnavailableError):
            downloader.acquire(track_meta)

    def test_missing_config_uses_friendly_message(
        self, track_meta: SpotifyTrackMetadata
    ) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            temp_dir=Path("/tmp"),
        )
        with pytest.raises(AudioProviderUnavailableError) as exc_info:
            downloader.acquire(track_meta)
        assert "RapidAPI" not in exc_info.value.detail
        assert "temporarily unavailable" in exc_info.value.detail.lower()

    def test_partial_config_still_fails(self, track_meta: SpotifyTrackMetadata) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="valid_key",
            api_host="",
            base_url="https://valid.url",
            temp_dir=Path("/tmp"),
        )
        with pytest.raises(AudioProviderUnavailableError):
            downloader.acquire(track_meta)

    def test_configured_provider_passes_config_to_requests(
        self, track_meta: SpotifyTrackMetadata
    ) -> None:
        from unittest.mock import patch

        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="test_key_abc",
            api_host="test-host.p.rapidapi.com",
            base_url="https://test-host.p.rapidapi.com",
            temp_dir=Path("/tmp"),
        )
        mock_acquired = AcquiredAudio(
            local_path=Path("/tmp/test.mp3"),
            mime_type="audio/mpeg",
            provider="test",
            temporary=True,
        )
        with patch.object(downloader, "_request_download_url") as mock_request:
            with patch.object(downloader, "_download_file") as mock_download:
                mock_request.return_value = "https://cdn.example.com/audio.mp3"
                mock_download.return_value = mock_acquired
                result = downloader.acquire(track_meta)
                mock_request.assert_called_once_with("abc123")
                assert result is mock_acquired

    def test_validate_download_url_rejects_invalid_scheme(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        with pytest.raises(InvalidDownloadedAudioError, match="Invalid download URL"):
            downloader._validate_download_url("ftp://malicious.com/audio.mp3")

    def test_validate_download_url_accepts_https(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        downloader._validate_download_url("https://cdn.example.com/audio.mp3")

    def test_validate_download_url_rejects_file_scheme(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        with pytest.raises(InvalidDownloadedAudioError):
            downloader._validate_download_url("file:///etc/passwd")

    def test_download_headers_satisfy_provider_cdn_requirements(self) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            _DOWNLOAD_HEADERS,
        )

        assert _DOWNLOAD_HEADERS["User-Agent"].startswith("Mozilla/5.0")
        assert _DOWNLOAD_HEADERS["Referer"] == "https://spotifydown.com/"
        assert "audio/mpeg" in _DOWNLOAD_HEADERS["Accept"]

    # ------------------------------------------------------------------
    # typed parser using RapidApiDownloadResponse Pydantic model
    # ------------------------------------------------------------------

    def test_parse_valid_success_response(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        payload = json.loads((FIXTURES_DIR / "download_song_success.json").read_text())
        url = downloader._parse_download_response(payload)
        assert url == "https://cdn.example.com/spotify/download/abc123.mp3"

    def test_parse_error_response_raises_not_found(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        payload = json.loads((FIXTURES_DIR / "download_song_error.json").read_text())
        with pytest.raises(AudioDownloadNotFoundError, match="Invalid Song Id"):
            downloader._parse_download_response(payload)

    def test_parse_missing_download_link_raises_not_found(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        payload = json.loads(
            (FIXTURES_DIR / "download_song_missing_field.json").read_text()
        )
        with pytest.raises(AudioDownloadNotFoundError, match="Download URL not found"):
            downloader._parse_download_response(payload)

    def test_parse_null_data_raises_not_found(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        payload = json.loads(
            (FIXTURES_DIR / "download_song_malformed.json").read_text()
        )
        with pytest.raises(AudioDownloadNotFoundError, match="Download URL not found"):
            downloader._parse_download_response(payload)

    def test_parse_invalid_payload_raises_invalid_audio(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        with pytest.raises(
            InvalidDownloadedAudioError,
            match=r"Invalid response format from audio provider.",
        ):
            downloader._parse_download_response({"not_a_url": "something"})

    def test_parse_unknown_extra_field_is_ignored(self, tmp_path: Path) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )
        result = downloader._parse_download_response(
            {
                "success": True,
                "data": {
                    "downloadLink": "https://ok.com/track.mp3",
                    "providerMetadata": "new-field",
                },
                "unknown_field": "should_not_break_existing_clients",
            }
        )
        assert result == "https://ok.com/track.mp3"

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            (
                {
                    "status": "success",
                    "result": {"downloadUrl": "https://ok.com/a.mp3"},
                },
                "https://ok.com/a.mp3",
            ),
            (
                {"success": 1, "data": {"download_url": "https://ok.com/b.mp3"}},
                "https://ok.com/b.mp3",
            ),
            (
                {"success": True, "url": "https://ok.com/c.mp3"},
                "https://ok.com/c.mp3",
            ),
            (
                {"status": 200, "data": "https://ok.com/d.mp3"},
                "https://ok.com/d.mp3",
            ),
        ],
    )
    def test_parse_supported_provider_response_variants(
        self,
        tmp_path: Path,
        payload: dict[str, object],
        expected: str,
    ) -> None:
        from app.infrastructure.spotify.rapidapi_downloader import (
            RapidApiSpotifyDownloaderProvider,
        )

        downloader = RapidApiSpotifyDownloaderProvider(
            api_key="key",
            api_host="host.com",
            base_url="https://host.com",
            temp_dir=tmp_path,
        )

        assert downloader._parse_download_response(payload) == expected


class TestSpotifyAnalysisService:
    @pytest.fixture
    def mock_spotify_metadata_a(self) -> SpotifyTrackMetadata:
        return SpotifyTrackMetadata(
            spotify_id="id_a",
            spotify_url="https://open.spotify.com/track/id_a",
            title="Track A",
            artists=("Artist A",),
            album="Album A",
            duration_ms=240000,
        )

    @pytest.fixture
    def mock_spotify_metadata_b(self) -> SpotifyTrackMetadata:
        return SpotifyTrackMetadata(
            spotify_id="id_b",
            spotify_url="https://open.spotify.com/track/id_b",
            title="Track B",
            artists=("Artist B",),
            album="Album B",
            duration_ms=180000,
        )

    def test_cleanup_removes_temp_file(self, tmp_path: Path) -> None:
        acquired = AcquiredAudio(
            local_path=tmp_path / "cleanup_test.mp3",
            mime_type="audio/mpeg",
            provider="test",
            temporary=True,
        )
        acquired.local_path.write_text("test")
        assert acquired.local_path.exists()

        service = SpotifyAnalysisService()
        service._cleanup(acquired)
        assert not acquired.local_path.exists()

    def test_cleanup_idempotent(self, tmp_path: Path) -> None:
        acquired = AcquiredAudio(
            local_path=tmp_path / "nonexistent.mp3",
            mime_type="audio/mpeg",
            provider="test",
            temporary=True,
        )
        service = SpotifyAnalysisService()
        service._cleanup(acquired)

    def test_normalizes_audio_not_supported_by_soundfile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import subprocess

        import numpy as np
        import soundfile as sf

        source = tmp_path / "provider_payload.mp3"
        source.write_bytes(b"valid-provider-container-placeholder")
        acquired = AcquiredAudio(
            local_path=source,
            mime_type="application/octet-stream",
            provider="test",
            temporary=True,
        )

        def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess:
            output = Path(command[-1])
            sf.write(output, np.zeros(22050, dtype=np.float32), 22050)
            return subprocess.CompletedProcess(command, 0)

        monkeypatch.setattr(subprocess, "run", fake_run)

        service = SpotifyAnalysisService()
        service._ensure_decodable_audio(acquired, "track_a")

        assert acquired.local_path.suffix == ".wav"
        assert acquired.local_path.exists()
        assert acquired.mime_type == "audio/wav"
        assert not source.exists()
        service._cleanup(acquired)

    def test_duration_validation_within_tolerance(self, tmp_path: Path) -> None:
        import numpy as np
        import soundfile as sf

        audio_path = tmp_path / "test_240s.wav"
        samplerate = 22050
        duration_samples = samplerate * 238
        data = np.zeros(duration_samples, dtype=np.float32)
        sf.write(str(audio_path), data, samplerate)

        acquired = AcquiredAudio(
            local_path=audio_path,
            mime_type="audio/wav",
            provider="test",
            temporary=True,
        )
        metadata = SpotifyTrackMetadata(
            spotify_id="test",
            spotify_url="",
            title="Test",
            artists=("A",),
            album="A",
            duration_ms=240000,
        )

        service = SpotifyAnalysisService()
        service._validate_audio_length(acquired, metadata, "track_a")

    def test_duration_validation_exceeds_tolerance(self, tmp_path: Path) -> None:
        import numpy as np
        import soundfile as sf

        audio_path = tmp_path / "test_200s.wav"
        samplerate = 22050
        duration_samples = samplerate * 200
        data = np.zeros(duration_samples, dtype=np.float32)
        sf.write(str(audio_path), data, samplerate)

        acquired = AcquiredAudio(
            local_path=audio_path,
            mime_type="audio/wav",
            provider="test",
            temporary=True,
        )
        metadata = SpotifyTrackMetadata(
            spotify_id="test",
            spotify_url="",
            title="Test",
            artists=("A",),
            album="A",
            duration_ms=240000,
        )

        service = SpotifyAnalysisService()
        with pytest.raises(AudioDurationMismatchError):
            service._validate_audio_length(acquired, metadata, "track_a")

    def test_duration_validation_warning_range(self, tmp_path: Path) -> None:
        import numpy as np
        import soundfile as sf

        audio_path = tmp_path / "test_232s.wav"
        samplerate = 22050
        duration_samples = samplerate * 232
        data = np.zeros(duration_samples, dtype=np.float32)
        sf.write(str(audio_path), data, samplerate)

        acquired = AcquiredAudio(
            local_path=audio_path,
            mime_type="audio/wav",
            provider="test",
            temporary=True,
        )
        metadata = SpotifyTrackMetadata(
            spotify_id="test",
            spotify_url="",
            title="Test",
            artists=("A",),
            album="A",
            duration_ms=240000,
        )

        service = SpotifyAnalysisService()
        service._validate_audio_length(acquired, metadata, "track_a")
