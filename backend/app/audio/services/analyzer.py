from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from app.core.exceptions import AudioAnalysisException
from app.schemas.audio import AudioAnalysis


class AudioAnalyzer:
    """Analyze audio files and extract audio features using Librosa."""

    def analyze(self, audio_path: Path) -> AudioAnalysis:
        """
        Analyze an audio file and extract its main characteristics.

        Parameters
        ----------
        audio_path : Path
            Path to the audio file.

        Returns
        -------
        AudioAnalysis
            Structured audio analysis containing duration, sample rate,
            BPM and RMS energy.
        """

        try:
            audio_data, sample_rate = librosa.load(
                audio_path,
                sr=None,
                mono=True,
            )

            duration = librosa.get_duration(
                y=audio_data,
                sr=sample_rate,
            )

            tempo, _ = librosa.beat.beat_track(
                y=audio_data,
                sr=sample_rate,
            )

            rms = librosa.feature.rms(
                y=audio_data,
            )

        except (
            librosa.util.exceptions.ParameterError,
            sf.LibsndfileError,
            OSError,
            ValueError,
        ) as exc:
            raise AudioAnalysisException(audio_path.name) from exc

        # ------------------------------------------------------------------
        # Librosa compatibility
        #
        # Depending on the installed version, beat_track() may return:
        #
        # float
        # numpy.float64
        # numpy.ndarray([tempo])
        #
        # This block normalizes every case into a Python float.
        # ------------------------------------------------------------------

        tempo = np.asarray(tempo).reshape(-1)[0]
        bpm = round(float(tempo), 2)

        energy = round(float(np.mean(rms)), 4)

        return AudioAnalysis(
            filename=audio_path.name,
            duration=round(float(duration), 2),
            sample_rate=int(sample_rate),
            bpm=bpm,
            energy=energy,
        )
