import asyncio
from io import BytesIO

from app.api.v1.endpoints import analysis as analysis_module
from app.application.dto.api import UploadAnalysisResponse
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


def test_analysis_status_returns_service_information() -> None:
    result = asyncio.run(analysis_module.analysis_status())

    assert result == {
        "service": "Analysis Service",
        "status": "available",
    }


def test_analyze_tracks_returns_analysis_response(monkeypatch) -> None:
    track_a = UploadFile(filename="Animals.mp3", file=BytesIO(b"a"))
    track_b = UploadFile(filename="Spaceman.mp3", file=BytesIO(b"b"))

    expected = UploadAnalysisResponse(
        status="success",
        message="Tracks analyzed successfully",
        analysis_id="test-session-123",
        track_a=AudioAnalysis(
            filename="Animals.mp3",
            duration=3.0,
            sample_rate=44100,
            bpm=128.01,
            energy=0.1823,
        ),
        track_b=AudioAnalysis(
            filename="Spaceman.mp3",
            duration=3.0,
            sample_rate=44100,
            bpm=127.94,
            energy=0.1907,
        ),
        compatibility=CompatibilityResult(
            compatibility_score=100.0,
            tempo_difference=0.07,
            energy_difference=0.0084,
            tempo_match="Excellent",
            energy_match="Excellent",
            harmonic_match="Excellent",
            overall_rating="Excellent",
        ),
        ai_recommendation=AIRecommendationResponse(
            summary="Strong pairing with excellent compatibility.",
            mix_direction="Blend Track B after a clean phrase-matched transition.",
            transition_quality="High",
            transition_type="Long harmonic blend",
            confidence=96,
            tempo_analysis=TempoAnalysis(
                difference="Only 0.07 BPM apart — excellent tempo alignment.",
                recommendation=(
                    "Use key lock and blend directly with no tempo adjustment."
                ),
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
            club_tip=(
                "Enter on the next 16-bar phrase to keep the dance floor locked in."
            ),
            professional_notes="Textbook blend with no risks identified.",
            risks=["None identified."],
            best_use_case="Peak-time or warm-up.",
            risk_level="Low",
        ),
        waveforms=Waveforms(
            track_a=WaveformResult(
                image_path="processed/analysis/test-session-123/waveform_track_a.png",
                width=1200,
                height=300,
            ),
            track_b=WaveformResult(
                image_path="processed/analysis/test-session-123/waveform_track_b.png",
                width=1200,
                height=300,
            ),
        ),
        spectrograms=Spectrograms(
            track_a=SpectrogramResult(
                image_path="processed/analysis/test-session-123/spectrogram_track_a.png",
                width=1200,
                height=500,
            ),
            track_b=SpectrogramResult(
                image_path="processed/analysis/test-session-123/spectrogram_track_b.png",
                width=1200,
                height=500,
            ),
        ),
    )

    monkeypatch.setattr(
        analysis_module.analysis_service,
        "analyze",
        lambda _track_a, _track_b: expected,
    )

    result = asyncio.run(analysis_module.analyze_tracks(track_a, track_b))

    assert result == expected


def test_analyze_tracks_http_response_includes_spectrograms(monkeypatch) -> None:
    expected = UploadAnalysisResponse(
        status="success",
        message="Tracks analyzed successfully",
        analysis_id="test-session-456",
        track_a=AudioAnalysis(
            filename="Animals.mp3",
            duration=3.0,
            sample_rate=44100,
            bpm=128.01,
            energy=0.1823,
        ),
        track_b=AudioAnalysis(
            filename="Spaceman.mp3",
            duration=3.0,
            sample_rate=44100,
            bpm=127.94,
            energy=0.1907,
        ),
        compatibility=CompatibilityResult(
            compatibility_score=100.0,
            tempo_difference=0.07,
            energy_difference=0.0084,
            tempo_match="Excellent",
            energy_match="Excellent",
            harmonic_match="Excellent",
            overall_rating="Excellent",
        ),
        ai_recommendation=AIRecommendationResponse(
            summary="Strong pairing with excellent compatibility.",
            mix_direction="Blend Track B after a clean phrase-matched transition.",
            transition_quality="High",
            transition_type="Long harmonic blend",
            confidence=96,
            tempo_analysis=TempoAnalysis(
                difference="Only 0.07 BPM apart — excellent tempo alignment.",
                recommendation=(
                    "Use key lock and blend directly with no tempo adjustment."
                ),
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
            club_tip=(
                "Enter on the next 16-bar phrase to keep the dance floor locked in."
            ),
            professional_notes="Textbook blend with no risks identified.",
            risks=["None identified."],
            best_use_case="Peak-time or warm-up.",
            risk_level="Low",
        ),
        waveforms=Waveforms(
            track_a=WaveformResult(
                image_path="processed/analysis/test-session-456/waveform_track_a.png",
                width=1200,
                height=300,
            ),
            track_b=WaveformResult(
                image_path="processed/analysis/test-session-456/waveform_track_b.png",
                width=1200,
                height=300,
            ),
        ),
        spectrograms=Spectrograms(
            track_a=SpectrogramResult(
                image_path="processed/analysis/test-session-456/spectrogram_track_a.png",
                width=1200,
                height=500,
            ),
            track_b=SpectrogramResult(
                image_path="processed/analysis/test-session-456/spectrogram_track_b.png",
                width=1200,
                height=500,
            ),
        ),
    )

    monkeypatch.setattr(
        analysis_module.analysis_service,
        "analyze",
        lambda _track_a, _track_b: expected,
    )

    client = TestClient(app)
    response = client.post(
        "/api/v1/analysis/analyze",
        files={
            "track_a": ("Animals.mp3", b"a", "audio/mpeg"),
            "track_b": ("Spaceman.mp3", b"b", "audio/mpeg"),
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert (
        body["spectrograms"]["track_a"]["image_path"]
        == "processed/analysis/test-session-456/spectrogram_track_a.png"
    )
    assert body["spectrograms"]["track_a"]["width"] == 1200
    assert body["spectrograms"]["track_b"]["height"] == 500
