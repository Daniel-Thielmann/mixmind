import numpy as np
import soundfile as sf
from app.audio.services.spectrogram import SpectrogramGenerator


def test_spectrogram_generator_creates_png_and_directory(tmp_path, monkeypatch) -> None:
    audio_path = tmp_path / "track.wav"
    sample_rate = 44100
    duration_seconds = 1.0
    time = np.linspace(
        0.0,
        duration_seconds,
        int(sample_rate * duration_seconds),
        endpoint=False,
    )
    waveform = 0.2 * np.sin(2 * np.pi * 128.0 * time)
    stereo = np.column_stack([waveform, waveform])
    sf.write(audio_path, stereo, sample_rate)

    from app.audio.services import base_image_generator

    processed_root = tmp_path / "processed"
    monkeypatch.setattr(
        base_image_generator,
        "settings",
        type(
            "SettingsStub",
            (),
            {
                "processed_path": processed_root,
                "analysis_path": processed_root / "analysis",
                "BASE_URL": "http://localhost:8000",
            },
        )(),
    )

    generator = SpectrogramGenerator()
    analysis_id = "test-session-xyz"
    result = generator.generate(audio_path, analysis_id, "b")

    generated_path = (
        processed_root / "analysis" / analysis_id / "spectrogram_track_b.png"
    )

    assert processed_root.joinpath("analysis", analysis_id).exists()
    assert generated_path.exists()
    assert (
        result.image_path == f"processed/analysis/{analysis_id}/spectrogram_track_b.png"
    )
    assert result.width == 1200
    assert result.height == 500

    from PIL import Image

    assert Image.open(generated_path).size == (1200, 500)
