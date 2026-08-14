import struct
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile

from app.application.use_cases.analysis.analyze_track import AnalysisService
from app.application.use_cases.analysis.progress import (
    AnalysisProgressEvent,
    AnalysisStage,
)
from app.domain.entities.track import AudioAnalysis
from app.domain.value_objects.compatibility import CompatibilityResult
from app.domain.value_objects.visualization import SpectrogramResult, WaveformResult
from app.infrastructure.llm.schemas import (
    AIRecommendationResponse,
    CompatibilityAnalysis,
    DJExecution,
    EnergyAnalysis,
    MixStrategy,
    TempoAnalysis,
)


def _write_silent_wav(
    path: Path, sample_rate: int = 44100, duration_secs: float = 0.5
) -> None:
    num_samples = int(sample_rate * duration_secs)
    data_size = num_samples * 2
    with path.open("wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<H", 1))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", sample_rate * 2))
        f.write(struct.pack("<H", 2))
        f.write(struct.pack("<H", 16))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(b"\x00\x00" * num_samples)


class FakeStorageService:
    def __init__(self, path_a: Path, path_b: Path) -> None:
        self._paths = [path_a, path_b]
        self._index = 0

    def save_audio(self, file: UploadFile) -> Path:
        path = self._paths[self._index]
        self._index += 1
        _write_silent_wav(path)
        return path


class FakeAudioAnalyzer:
    def analyze(self, audio_path: Path, **kwargs: object) -> AudioAnalysis:
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
            harmonic_match="Excellent",
            overall_rating="Excellent",
        )


class FakeWaveformGenerator:
    def __init__(self, output_paths: list[str]) -> None:
        self._output_paths = output_paths
        self._index = 0

    def generate(self, audio_path: Path, **kwargs: object) -> WaveformResult:
        image_path = self._output_paths[self._index]
        self._index += 1
        return WaveformResult(image_path=image_path, width=1200, height=300)


class FakeSpectrogramGenerator:
    def __init__(self, output_paths: list[str]) -> None:
        self._output_paths = output_paths
        self._index = 0

    def generate(self, audio_path: Path, **kwargs: object) -> SpectrogramResult:
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

    progress_events: list[AnalysisProgressEvent] = []
    response = service.analyze(track_a, track_b, on_progress=progress_events.append)

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
    assert [event.stage for event in progress_events] == [
        AnalysisStage.STARTED,
        AnalysisStage.FILES_SAVED,
        AnalysisStage.TRACK_A_ANALYZED,
        AnalysisStage.TRACK_B_ANALYZED,
        AnalysisStage.COMPATIBILITY_COMPUTED,
        AnalysisStage.AI_RECOMMENDATION_STARTED,
        AnalysisStage.COMPLETED,
    ]
    assert [event.progress for event in progress_events] == sorted(
        event.progress for event in progress_events
    )
    assert progress_events[-1].data == response.model_dump(mode="json")
