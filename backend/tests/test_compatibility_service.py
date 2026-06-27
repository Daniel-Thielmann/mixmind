from app.schemas.audio import AudioAnalysis
from app.services.compatibility_service import CompatibilityService


def test_compare_returns_high_compatibility_for_similar_tracks() -> None:
    service = CompatibilityService()

    track_a = AudioAnalysis(
        filename="Animals.mp3",
        duration=302.18,
        sample_rate=44100,
        bpm=128.01,
        energy=0.1823,
    )
    track_b = AudioAnalysis(
        filename="Spaceman.mp3",
        duration=295.72,
        sample_rate=44100,
        bpm=127.94,
        energy=0.1907,
    )

    result = service.compare(track_a, track_b)

    assert result.compatibility_score > 90
    assert result.tempo_match == "Excellent"
    assert result.energy_match == "Excellent"
