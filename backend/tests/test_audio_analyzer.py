import numpy as np
import soundfile as sf
from app.audio.services.analyzer import AudioAnalyzer


def test_audio_analyzer_extracts_audio_metrics(tmp_path) -> None:
    audio_path = tmp_path / "track.wav"
    sample_rate = 44100
    duration_seconds = 2.0
    time = np.linspace(
        0.0, duration_seconds, int(sample_rate * duration_seconds), endpoint=False
    )
    waveform = 0.2 * np.sin(2 * np.pi * 128.0 * time)
    stereo = np.column_stack([waveform, waveform])
    sf.write(audio_path, stereo, sample_rate)

    result = AudioAnalyzer().analyze(audio_path)

    assert result.filename == "track.wav"
    assert result.sample_rate == sample_rate
    assert result.duration == 2.0
    assert result.energy > 0
