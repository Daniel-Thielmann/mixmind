"""Energy measurements for audio signals."""

import numpy as np
from numpy.typing import NDArray


def calculate_windowed_rms(
    audio: NDArray[np.float32],
    window_size: int,
) -> NDArray[np.float32]:
    """Return one RMS value for each complete, non-overlapping window.

    Parameters
    ----------
    audio:
        One-dimensional mono audio signal.
    window_size:
        Number of samples in each window. It must be positive.

    Returns
    -------
    numpy.ndarray
        One float32 RMS value per complete window. Samples in an incomplete
        final window are intentionally ignored in this first implementation.
    """
    if audio.ndim != 1:
        raise ValueError("audio must be a one-dimensional mono signal")
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    complete_window_count = audio.size // window_size
    rms_values = np.empty(complete_window_count, dtype=np.float32)

    for window_index in range(complete_window_count):
        start = window_index * window_size
        end = start + window_size
        window = audio[start:end]

        squared_samples = np.square(window)
        mean_square = np.mean(squared_samples)
        rms = np.sqrt(mean_square)

        rms_values[window_index] = rms

    return rms_values
