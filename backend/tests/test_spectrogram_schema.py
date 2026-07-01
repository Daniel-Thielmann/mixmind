from app.schemas.spectrogram import SpectrogramResult, Spectrograms


def test_spectrogram_schema_serialization() -> None:
    result = SpectrogramResult(
        image_path="processed/analysis/test/spectrogram_track_a.png",
        url="http://localhost:8000/static/analysis/test/spectrogram_track_a.png",
        width=1200,
        height=500,
    )
    payload = Spectrograms(track_a=result, track_b=result)

    assert (
        payload.track_a.image_path == "processed/analysis/test/spectrogram_track_a.png"
    )
    assert (
        payload.track_a.url
        == "http://localhost:8000/static/analysis/test/spectrogram_track_a.png"
    )
    assert payload.track_a.width == 1200
    assert payload.track_a.height == 500
    assert (
        payload.model_dump()["track_b"]["image_path"]
        == "processed/analysis/test/spectrogram_track_a.png"
    )
