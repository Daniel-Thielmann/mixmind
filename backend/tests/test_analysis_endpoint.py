import asyncio
from io import BytesIO

from app.api.v1.endpoints import analysis as analysis_module
from app.main import app
from app.schemas.api import UploadAnalysisResponse
from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from app.schemas.spectrogram import SpectrogramResult, Spectrograms
from app.schemas.waveform import WaveformResult, Waveforms
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
            overall_rating="Excellent",
        ),
        waveforms=Waveforms(
            track_a=WaveformResult(
                image_path="processed/analysis/test-session-123/waveform_track_a.png",
                url="http://localhost:8000/static/analysis/test-session-123/waveform_track_a.png",
                width=1200,
                height=300,
            ),
            track_b=WaveformResult(
                image_path="processed/analysis/test-session-123/waveform_track_b.png",
                url="http://localhost:8000/static/analysis/test-session-123/waveform_track_b.png",
                width=1200,
                height=300,
            ),
        ),
        spectrograms=Spectrograms(
            track_a=SpectrogramResult(
                image_path="processed/analysis/test-session-123/spectrogram_track_a.png",
                url="http://localhost:8000/static/analysis/test-session-123/spectrogram_track_a.png",
                width=1200,
                height=500,
            ),
            track_b=SpectrogramResult(
                image_path="processed/analysis/test-session-123/spectrogram_track_b.png",
                url="http://localhost:8000/static/analysis/test-session-123/spectrogram_track_b.png",
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
            overall_rating="Excellent",
        ),
        waveforms=Waveforms(
            track_a=WaveformResult(
                image_path="processed/analysis/test-session-456/waveform_track_a.png",
                url="http://localhost:8000/static/analysis/test-session-456/waveform_track_a.png",
                width=1200,
                height=300,
            ),
            track_b=WaveformResult(
                image_path="processed/analysis/test-session-456/waveform_track_b.png",
                url="http://localhost:8000/static/analysis/test-session-456/waveform_track_b.png",
                width=1200,
                height=300,
            ),
        ),
        spectrograms=Spectrograms(
            track_a=SpectrogramResult(
                image_path="processed/analysis/test-session-456/spectrogram_track_a.png",
                url="http://localhost:8000/static/analysis/test-session-456/spectrogram_track_a.png",
                width=1200,
                height=500,
            ),
            track_b=SpectrogramResult(
                image_path="processed/analysis/test-session-456/spectrogram_track_b.png",
                url="http://localhost:8000/static/analysis/test-session-456/spectrogram_track_b.png",
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
