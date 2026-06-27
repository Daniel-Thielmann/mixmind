from pathlib import Path

import librosa
import soundfile as sf

from app.core.exceptions import AudioAnalysisException
from app.schemas.audio import AudioAnalysis


class AudioAnalyzer:
    """Analyze audio files and extract the metrics required by the API."""

    def analyze(self, audio_path: Path) -> AudioAnalysis:
        """Load audio with Librosa and return a structured analysis result."""

        try:
            audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
            duration = librosa.get_duration(y=audio_data, sr=sample_rate)
            bpm, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
            rms = librosa.feature.rms(y=audio_data)
        except (
            librosa.util.exceptions.ParameterError,
            sf.LibsndfileError,
            OSError,
            ValueError,
        ) as exc:
            raise AudioAnalysisException(audio_path.name) from exc

        energy = float(rms.mean())

        return AudioAnalysis(
            filename=audio_path.name,
            duration=round(float(duration), 2),
            sample_rate=int(sample_rate),
            bpm=round(float(bpm), 2),
            energy=round(energy, 4),
        )
