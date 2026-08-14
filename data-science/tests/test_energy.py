import numpy as np
import pytest

from mixmind_ds.energy import calculate_windowed_rms


def test_calculate_windowed_rms_returns_one_value_per_complete_window() -> None:
    audio = np.array(
        [
            0.0,
            0.2,
            -0.2,
            0.0,
            0.5,
            -0.5,
            0.5,
            -0.5,
            0.1,
            -0.1,
            0.1,
            -0.1,
        ],
        dtype=np.float32,
    )

    result = calculate_windowed_rms(audio, window_size=4)

    expected = np.array([0.14142136, 0.5, 0.1], dtype=np.float32)
    np.testing.assert_allclose(result, expected, rtol=1e-6)
    assert result.dtype == np.float32


def test_calculate_windowed_rms_ignores_an_incomplete_final_window() -> None:
    audio = np.array([1.0, -1.0, 0.5, 99.0], dtype=np.float32)

    result = calculate_windowed_rms(audio, window_size=3)

    expected = np.array([np.sqrt(0.75)], dtype=np.float32)
    np.testing.assert_allclose(result, expected, rtol=1e-6)


@pytest.mark.parametrize("window_size", [0, -1])
def test_calculate_windowed_rms_rejects_non_positive_window_size(
    window_size: int,
) -> None:
    audio = np.array([0.0, 1.0], dtype=np.float32)

    with pytest.raises(ValueError, match="window_size must be positive"):
        calculate_windowed_rms(audio, window_size)
