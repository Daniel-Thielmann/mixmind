import asyncio
from io import BytesIO

from app.api.v1.endpoints import analysis as analysis_module
from app.schemas.api import UploadAnalysisResponse
from app.schemas.audio import AudioAnalysis
from app.schemas.recommendation import CompatibilityResult
from fastapi import UploadFile


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
    )

    monkeypatch.setattr(
        analysis_module.analysis_service,
        "analyze",
        lambda _track_a, _track_b: expected,
    )

    result = asyncio.run(analysis_module.analyze_tracks(track_a, track_b))

    assert result == expected
