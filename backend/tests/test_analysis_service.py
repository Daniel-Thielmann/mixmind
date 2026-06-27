from io import BytesIO
from pathlib import Path

from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.services.analysis_service import AnalysisService
from fastapi import UploadFile


class FakeStorageService:
    def __init__(self, path_a: Path, path_b: Path) -> None:
        self._paths = [path_a, path_b]
        self._index = 0

    def save_audio(self, file: UploadFile) -> Path:
        path = self._paths[self._index]
        self._index += 1
        path.write_bytes(file.file.read() or b"audio")
        file.file.seek(0)
        return path


class FakeAudioAnalyzer:
    def analyze(self, audio_path: Path) -> AudioAnalysis:
        return AudioAnalysis(
            filename=audio_path.name,
            duration=3.0,
            sample_rate=44100,
            bpm=128.0,
            energy=0.18,
        )


class FakeCompatibilityService:
    def compare(
        self,
        track_a: AudioAnalysis,
        track_b: AudioAnalysis,
    ) -> CompatibilityResult:
        return CompatibilityResult(
            compatibility_score=96.0,
            tempo_difference=0.0,
            energy_difference=0.0,
            tempo_match="Excellent",
            energy_match="Excellent",
            overall_rating="Excellent",
        )


def test_analysis_service_analyze_builds_complete_response(tmp_path) -> None:
    path_a = tmp_path / "track_a.wav"
    path_b = tmp_path / "track_b.wav"

    service = AnalysisService(
        storage=FakeStorageService(path_a, path_b),
        analyzer=FakeAudioAnalyzer(),
        compatibility=FakeCompatibilityService(),
    )

    track_a = UploadFile(filename="Animals.mp3", file=BytesIO(b"a"))
    track_b = UploadFile(filename="Spaceman.mp3", file=BytesIO(b"b"))

    response = service.analyze(track_a, track_b)

    assert response.status == "success"
    assert response.track_a.filename == "Animals.mp3"
    assert response.track_b.filename == "Spaceman.mp3"
    assert response.compatibility.compatibility_score == 96.0
