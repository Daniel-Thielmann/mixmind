from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
from app.audio.services.base_image_generator import BaseImageGenerator
from app.schemas.waveform import WaveformResult


class WaveformGenerator(BaseImageGenerator):
    """Generate and persist waveform images for analyzed audio files."""

    def __init__(self) -> None:
        super().__init__(image_width=1200, image_height=300)

    @property
    def _subdir_prefix(self) -> str:
        return "waveform"

    def generate(
        self,
        audio_path: Path,
        analysis_id: str,
        track_label: str,
    ) -> WaveformResult:
        """Render the waveform for an audio file and save it as PNG."""

        audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=True)
        filename = self._build_filename(track_label)
        analysis_dir = self._ensure_analysis_dir(analysis_id)
        image_path = analysis_dir / filename

        figure = plt.figure(figsize=(12, 3), dpi=100)
        axis = figure.add_subplot(111)
        librosa.display.waveshow(audio_data, sr=sample_rate, ax=axis)
        axis.set_axis_off()
        figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        figure.savefig(str(image_path), dpi=100)
        plt.close(figure)

        return WaveformResult(
            image_path=self._build_relative_path(analysis_id, filename),
            url=self._build_url(analysis_id, filename),
            width=self._image_width,
            height=self._image_height,
        )


waveform_generator = WaveformGenerator()
