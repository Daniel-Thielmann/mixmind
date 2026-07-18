import json
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track import AnalysisService
from app.domain.entities.track import AudioAnalysis
from app.domain.value_objects.compatibility import CompatibilityResult
from app.domain.value_objects.visualization import (
    SpectrogramResult,
    Spectrograms,
    WaveformResult,
    Waveforms,
)
from app.infrastructure.llm.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.main import app
from fastapi import UploadFile
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeStorage:
    def __init__(self, base: Path) -> None:
        self._base = base

    def save_audio(self, file: UploadFile) -> Path:
        path = self._base / (file.filename or "tmp.wav")
        path.write_bytes(file.file.read() or b"data")
        file.file.seek(0)
        return path


class FakeAnalyzer:
    def analyze(self, audio_path: Path) -> AudioAnalysis:
        return AudioAnalysis(
            filename=audio_path.name,
            duration=3.0,
            sample_rate=44100,
            bpm=128.0,
            energy=0.18,
        )


class FakeCompat:
    def compare(
        self, track_a: AudioAnalysis, track_b: AudioAnalysis
    ) -> CompatibilityResult:
        return CompatibilityResult(
            compatibility_score=96.0,
            tempo_difference=0.0,
            energy_difference=0.0,
            tempo_match="Excellent",
            energy_match="Excellent",
            harmonic_match="Excellent",
            overall_rating="Excellent",
        )


def make_fake_waveform(
    analysis_id: str, track_label: str, base_url: str
) -> WaveformResult:
    return WaveformResult(
        image_path=f"processed/analysis/{analysis_id}/waveform_track_{track_label}.png",
        url=f"{base_url}/static/analysis/{analysis_id}/waveform_track_{track_label}.png",
        width=1200,
        height=300,
    )


def make_fake_spectrogram(
    analysis_id: str, track_label: str, base_url: str
) -> SpectrogramResult:
    return SpectrogramResult(
        image_path=f"processed/analysis/{analysis_id}/spectrogram_track_{track_label}.png",
        url=f"{base_url}/static/analysis/{analysis_id}/spectrogram_track_{track_label}.png",
        width=1200,
        height=500,
    )


class FakeWaveformGen:
    def generate(
        self, audio_path: Path, analysis_id: str, track_label: str
    ) -> WaveformResult:
        return make_fake_waveform(analysis_id, track_label, "http://localhost:8000")


class FakeSpectrogramGen:
    def generate(
        self, audio_path: Path, analysis_id: str, track_label: str
    ) -> SpectrogramResult:
        return make_fake_spectrogram(analysis_id, track_label, "http://localhost:8000")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAnalysisSession:
    """Part 1 & 2 – Session folder and analysis.json generation."""

    def test_analysis_has_unique_analysis_id(self) -> None:
        ids: set[str] = set()

        for _ in range(10):
            service = AnalysisService(
                storage=FakeStorage(Path(".")),
                analyzer=FakeAnalyzer(),
                waveform_service=FakeWaveformGen(),
                spectrogram_service=FakeSpectrogramGen(),
                compatibility=FakeCompat(),
            )

            ta = UploadFile(filename="a.wav", file=BytesIO(b"a"))
            tb = UploadFile(filename="b.wav", file=BytesIO(b"b"))
            response = service.analyze(ta, tb)

            assert len(response.analysis_id) == 32  # uuid4().hex
            ids.add(response.analysis_id)

        assert len(ids) == 10  # all unique

    def test_analysis_creates_session_folder(self, tmp_path, monkeypatch) -> None:
        from app.application.use_cases.analysis import analyze_track as module

        processed_root = tmp_path / "processed"
        monkeypatch.setattr(
            module,
            "settings",
            SimpleNamespace(
                analysis_path=processed_root / "analysis",
                BASE_URL="http://testserver",
                processed_path=processed_root,
            ),
        )

        service = AnalysisService(
            storage=FakeStorage(tmp_path),
            analyzer=FakeAnalyzer(),
            waveform_service=FakeWaveformGen(),
            spectrogram_service=FakeSpectrogramGen(),
            compatibility=FakeCompat(),
        )

        ta = UploadFile(filename="a.wav", file=BytesIO(b"a"))
        tb = UploadFile(filename="b.wav", file=BytesIO(b"b"))
        result = service.analyze(ta, tb)

        folder = processed_root / "analysis" / result.analysis_id
        assert folder.exists()
        assert folder.is_dir()

    def test_analysis_json_is_generated(self, tmp_path, monkeypatch) -> None:
        from app.application.use_cases.analysis import analyze_track as module

        processed_root = tmp_path / "processed"
        monkeypatch.setattr(
            module,
            "settings",
            SimpleNamespace(
                analysis_path=processed_root / "analysis",
                BASE_URL="http://testserver",
                processed_path=processed_root,
            ),
        )

        service = AnalysisService(
            storage=FakeStorage(tmp_path),
            analyzer=FakeAnalyzer(),
            waveform_service=FakeWaveformGen(),
            spectrogram_service=FakeSpectrogramGen(),
            compatibility=FakeCompat(),
        )

        ta = UploadFile(filename="a.wav", file=BytesIO(b"a"))
        tb = UploadFile(filename="b.wav", file=BytesIO(b"b"))
        result = service.analyze(ta, tb)

        json_path = processed_root / "analysis" / result.analysis_id / "analysis.json"
        assert json_path.exists()

        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["analysis_id"] == result.analysis_id
        assert "track_a" in data
        assert "track_b" in data
        assert "compatibility" in data
        assert "waveforms" in data
        assert "spectrograms" in data

    def test_analysis_json_contains_all_fields(self, tmp_path, monkeypatch) -> None:
        from app.application.use_cases.analysis import analyze_track as module

        processed_root = tmp_path / "processed"
        monkeypatch.setattr(
            module,
            "settings",
            SimpleNamespace(
                analysis_path=processed_root / "analysis",
                BASE_URL="http://testserver",
                processed_path=processed_root,
            ),
        )

        service = AnalysisService(
            storage=FakeStorage(tmp_path),
            analyzer=FakeAnalyzer(),
            waveform_service=FakeWaveformGen(),
            spectrogram_service=FakeSpectrogramGen(),
            compatibility=FakeCompat(),
        )

        ta = UploadFile(filename="a.wav", file=BytesIO(b"a"))
        tb = UploadFile(filename="b.wav", file=BytesIO(b"b"))
        result = service.analyze(ta, tb)

        json_path = processed_root / "analysis" / result.analysis_id / "analysis.json"
        data = json.loads(json_path.read_text(encoding="utf-8"))

        assert data["analysis_id"] == result.analysis_id
        assert "filename" in data["track_a"]
        assert "bpm" in data["track_a"]
        assert "energy" in data["track_a"]
        assert "duration" in data["track_a"]
        assert "compatibility_score" in data["compatibility"]
        assert "url" in data["waveforms"]["track_a"]
        assert "url" in data["spectrograms"]["track_a"]


class TestPublicUrls:
    """Part 3 & 4 – Public URLs and StaticFiles."""

    def test_waveform_result_includes_url(self) -> None:
        result = WaveformResult(
            image_path="processed/analysis/test/waveform.png",
            url="http://localhost:8000/static/analysis/test/waveform.png",
            width=1200,
            height=300,
        )

        assert result.url == "http://localhost:8000/static/analysis/test/waveform.png"

    def test_spectrogram_result_includes_url(self) -> None:
        result = SpectrogramResult(
            image_path="processed/analysis/test/spectrogram.png",
            url="http://localhost:8000/static/analysis/test/spectrogram.png",
            width=1200,
            height=500,
        )

        assert (
            result.url == "http://localhost:8000/static/analysis/test/spectrogram.png"
        )

    def test_upload_response_includes_analysis_id(self) -> None:
        response = UploadAnalysisResponse(
            status="success",
            message="OK",
            analysis_id="abc123",
            track_a=AudioAnalysis(
                filename="a.mp3",
                duration=1.0,
                sample_rate=44100,
                bpm=120.0,
                energy=0.1,
            ),
            track_b=AudioAnalysis(
                filename="b.mp3",
                duration=1.0,
                sample_rate=44100,
                bpm=120.0,
                energy=0.1,
            ),
            compatibility=CompatibilityResult(
                compatibility_score=100.0,
                tempo_difference=0.0,
                energy_difference=0.0,
                tempo_match="Excellent",
                energy_match="Excellent",
                harmonic_match="Excellent",
                overall_rating="Excellent",
            ),
            ai_recommendation=AIRecommendationResponse(
                summary="",
                mix_direction="",
                transition_quality="",
                transition_type="",
                confidence=0,
                tempo_analysis=TempoAnalysis(difference="", recommendation=""),
                energy_analysis=EnergyAnalysis(difference="", recommendation=""),
                compatibility_analysis=CompatibilityAnalysis(
                    score="", interpretation=""
                ),
                mix_strategy=MixStrategy(
                    before_transition="",
                    during_transition="",
                    after_transition="",
                ),
                dj_execution=DJExecution(
                    loop="",
                    eq="",
                    filter="",
                    tempo_fader="",
                    phrase_matching="",
                    cue_point="",
                ),
                club_tip="",
                professional_notes="",
                risks=[],
                best_use_case="",
                risk_level="",
            ),
            waveforms=Waveforms(
                track_a=WaveformResult(
                    image_path="a.png",
                    url="http://localhost:8000/static/a.png",
                    width=1200,
                    height=300,
                ),
                track_b=WaveformResult(
                    image_path="b.png",
                    url="http://localhost:8000/static/b.png",
                    width=1200,
                    height=300,
                ),
            ),
            spectrograms=Spectrograms(
                track_a=SpectrogramResult(
                    image_path="a.png",
                    url="http://localhost:8000/static/a.png",
                    width=1200,
                    height=500,
                ),
                track_b=SpectrogramResult(
                    image_path="b.png",
                    url="http://localhost:8000/static/b.png",
                    width=1200,
                    height=500,
                ),
            ),
        )

        assert response.analysis_id == "abc123"
        dump = response.model_dump()
        assert dump["analysis_id"] == "abc123"

    def test_static_files_mounted(self) -> None:
        client = TestClient(app)
        response = client.get("/static")
        assert response.status_code in (200, 404, 307)

    def test_api_response_returns_analysis_id(self, monkeypatch) -> None:
        from app.api.v1.endpoints import analysis as analysis_module

        expected = UploadAnalysisResponse(
            status="success",
            message="Tracks analyzed successfully",
            analysis_id="session-from-api",
            track_a=AudioAnalysis(
                filename="a.mp3",
                duration=1.0,
                sample_rate=44100,
                bpm=120.0,
                energy=0.1,
            ),
            track_b=AudioAnalysis(
                filename="b.mp3",
                duration=1.0,
                sample_rate=44100,
                bpm=120.0,
                energy=0.1,
            ),
            compatibility=CompatibilityResult(
                compatibility_score=100.0,
                tempo_difference=0.0,
                energy_difference=0.0,
                tempo_match="Excellent",
                energy_match="Excellent",
                harmonic_match="Excellent",
                overall_rating="Excellent",
            ),
            ai_recommendation=AIRecommendationResponse(
                summary="",
                mix_direction="",
                transition_quality="",
                transition_type="",
                confidence=0,
                tempo_analysis=TempoAnalysis(difference="", recommendation=""),
                energy_analysis=EnergyAnalysis(difference="", recommendation=""),
                compatibility_analysis=CompatibilityAnalysis(
                    score="", interpretation=""
                ),
                mix_strategy=MixStrategy(
                    before_transition="",
                    during_transition="",
                    after_transition="",
                ),
                dj_execution=DJExecution(
                    loop="",
                    eq="",
                    filter="",
                    tempo_fader="",
                    phrase_matching="",
                    cue_point="",
                ),
                club_tip="",
                professional_notes="",
                risks=[],
                best_use_case="",
                risk_level="",
            ),
            waveforms=Waveforms(
                track_a=WaveformResult(
                    image_path="a.png",
                    url="http://localhost:8000/static/a.png",
                    width=1200,
                    height=300,
                ),
                track_b=WaveformResult(
                    image_path="b.png",
                    url="http://localhost:8000/static/b.png",
                    width=1200,
                    height=300,
                ),
            ),
            spectrograms=Spectrograms(
                track_a=SpectrogramResult(
                    image_path="a.png",
                    url="http://localhost:8000/static/a.png",
                    width=1200,
                    height=500,
                ),
                track_b=SpectrogramResult(
                    image_path="b.png",
                    url="http://localhost:8000/static/b.png",
                    width=1200,
                    height=500,
                ),
            ),
        )

        monkeypatch.setattr(
            analysis_module.analysis_service,
            "analyze",
            lambda _a, _b: expected,
        )

        client = TestClient(app)
        response = client.post(
            "/api/v1/analysis/analyze",
            files={
                "track_a": ("a.mp3", b"x", "audio/mpeg"),
                "track_b": ("b.mp3", b"y", "audio/mpeg"),
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["analysis_id"] == "session-from-api"
