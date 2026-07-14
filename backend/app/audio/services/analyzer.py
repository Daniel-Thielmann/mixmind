from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from app.core.exceptions import AudioAnalysisException
from app.schemas.audio import AudioAnalysis


class AudioAnalyzer:
    """Analyze audio files and extract audio features using Librosa."""

    # Krumhansl-Schmuckler Profiles (Mathematical representation of musical scales)
    MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Camelot Wheel Mapping
    CAMELOT_WHEEL = {
        "B Major": "1B", "G# Minor": "1A",
        "F# Major": "2B", "D# Minor": "2A",
        "C# Major": "3B", "A# Minor": "3A",
        "G# Major": "4B", "F Minor": "4A",
        "D# Major": "5B", "C Minor": "5A",
        "A# Major": "6B", "G Minor": "6A",
        "F Major": "7B", "D Minor": "7A",
        "C Major": "8B", "A Minor": "8A",
        "G Major": "9B", "E Minor": "9A",
        "D Major": "10B", "B Minor": "10A",
        "A Major": "11B", "F# Minor": "11A",
        "E Major": "12B", "C# Minor": "12A",
    }

    def _detect_key(self, y: np.ndarray, sr: int) -> tuple[str, str]:
        """Calculates the musical key using the Krumhansl-Schmuckler algorithm."""
        
        # Extrai o cromagrama (Harmonic Pitch Class Profile) usando CQT
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_sum = np.sum(chroma, axis=1)

        major_correlations = []
        minor_correlations = []

        # Rotaciona os perfis e calcula a correlação de Pearson para as 12 notas
        for i in range(12):
            major_rot = np.roll(self.MAJOR_PROFILE, i)
            minor_rot = np.roll(self.MINOR_PROFILE, i)
            
            major_correlations.append(np.corrcoef(chroma_sum, major_rot)[0, 1])
            minor_correlations.append(np.corrcoef(chroma_sum, minor_rot)[0, 1])

        # Encontra a maior correlação para definir a Tônica e a Escala
        max_major_idx = np.argmax(major_correlations)
        max_minor_idx = np.argmax(minor_correlations)

        if major_correlations[max_major_idx] > minor_correlations[max_minor_idx]:
            return f"{self.NOTES[max_major_idx]} Major"
        else:
            return f"{self.NOTES[max_minor_idx]} Minor"


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
            BPM, RMS energy, Musical Key, and Camelot code.
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
            
            # EXTRAÇÃO HARMÔNICA
            detected_key = self._detect_key(audio_data, sample_rate)
            camelot_code = self.CAMELOT_WHEEL.get(detected_key, "Unknown")

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
            key=detected_key,        
            camelot=camelot_code,     
        )