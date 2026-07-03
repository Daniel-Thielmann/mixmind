from io import BytesIO
from pathlib import Path

from app.ai.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)
from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.schemas.spectrogram import SpectrogramResult
from app.schemas.waveform import WaveformResult
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


class FakeWaveformGenerator:
    def __init__(self, output_paths: list[str]) -> None:
        self._output_paths = output_paths
        self._index = 0

    def generate(self, audio_path: Path) -> WaveformResult:
        image_path = self._output_paths[self._index]
        self._index += 1
        return WaveformResult(image_path=image_path, width=1200, height=300)


class FakeSpectrogramGenerator:
    def __init__(self, output_paths: list[str]) -> None:
        self._output_paths = output_paths
        self._index = 0

    def generate(self, audio_path: Path) -> SpectrogramResult:
        image_path = self._output_paths[self._index]
        self._index += 1
        return SpectrogramResult(image_path=image_path, width=1200, height=500)


class FakeDJAgent:
    def recommend(self, recommendation) -> AIRecommendationResponse:
        return AIRecommendationResponse(
            summary="Strong pairing with excellent compatibility.",
            mix_direction="Blend with a long harmonic transition.",
            transition_quality="High",
            transition_type="Long harmonic blend",
            confidence=97,
            tempo_analysis=TempoAnalysis(
                difference="BPM difference is negligible.",
                recommendation="No tempo adjustment needed.",
            ),
            energy_analysis=EnergyAnalysis(
                difference="Energy delta is minimal.",
                recommendation="Maintain current energy curve.",
            ),
            compatibility_analysis=CompatibilityAnalysis(
                score="96/100 — Excellent.",
                interpretation="Backend rates this pair as Excellent.",
            ),
            mix_strategy=MixStrategy(
                before_transition="Set a 4-beat loop on Track B.",
                during_transition="Blend over 16 bars with EQ sweep.",
                after_transition="Release loop and ride the groove.",
            ),
            dj_execution=DJExecution(
                loop="4-beat loop on Track B entrance.",
                eq="Reduce lows on Track A over 8 bars.",
                filter="High-pass on Track A.",
                tempo_fader="No adjustment needed.",
                phrase_matching="Match 16-bar phrases.",
                cue_point="Set cue on first beat of bar 33.",
            ),
            club_tip="Enter on a phrase boundary to keep the floor engaged.",
            professional_notes="Textbook blend with no risks identified.",
            risks=["None identified."],
            best_use_case="Peak-time or warm-up.",
            risk_level="Low",
        )


def test_analysis_service_analyze_builds_complete_response(tmp_path) -> None:
    path_a = tmp_path / "track_a.wav"
    path_b = tmp_path / "track_b.wav"

    service = AnalysisService(
        storage=FakeStorageService(path_a, path_b),
        analyzer=FakeAudioAnalyzer(),
        waveform_service=FakeWaveformGenerator(
            [
                "processed/analysis/test-session/waveform_track_a.png",
                "processed/analysis/test-session/waveform_track_b.png",
            ]
        ),
        spectrogram_service=FakeSpectrogramGenerator(
            [
                "processed/analysis/test-session/spectrogram_track_a.png",
                "processed/analysis/test-session/spectrogram_track_b.png",
            ]
        ),
        compatibility=FakeCompatibilityService(),
        ai_agent=FakeDJAgent(),
    )

    track_a = UploadFile(filename="Animals.mp3", file=BytesIO(b"a"))
    track_b = UploadFile(filename="Spaceman.mp3", file=BytesIO(b"b"))

    response = service.analyze(track_a, track_b)

    assert response.status == "success"
    assert response.track_a.filename == "Animals.mp3"
    assert response.track_b.filename == "Spaceman.mp3"
    assert response.compatibility.compatibility_score == 96.0
    assert response.ai_recommendation.confidence == 97
    assert (
        response.ai_recommendation.summary
        == "Strong pairing with excellent compatibility."
    )
    assert response.ai_recommendation.risk_level == "Low"
    assert response.waveforms.track_a.width == 1200
    assert response.waveforms.track_b.height == 300
    assert response.spectrograms.track_a.width == 1200
    assert response.spectrograms.track_b.height == 500
