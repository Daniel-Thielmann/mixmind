import logging
import platform
import sys

import librosa
import numpy as np
import psutil

logger = logging.getLogger(__name__)


def get_memory_mb() -> float:
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def get_vms_mb() -> float:
    process = psutil.Process()
    return process.memory_info().vms / (1024 * 1024)


def log_memory(tag: str) -> None:
    mem = get_memory_mb()
    vms = get_vms_mb()
    logger.info(
        "Memory [%s]: RSS=%.2f MB | VMS=%.2f MB",
        tag,
        mem,
        vms,
    )


def log_memory_detail(tag: str, extra: str = "") -> None:
    mem = get_memory_mb()
    vms = get_vms_mb()
    process = psutil.Process()
    pf = process.memory_full_info()
    uss = pf.uss / (1024 * 1024) if hasattr(pf, "uss") and pf.uss else 0.0  # type: ignore[attr-defined]
    logger.info(
        "Memory [%s]: RSS=%.2f MB | VMS=%.2f MB | USS=%.2f MB%s",
        tag,
        mem,
        vms,
        uss,
        f" | {extra}" if extra else "",
    )


def log_library_versions() -> None:
    logger.info("=" * 60)
    logger.info("Library versions & environment:")
    logger.info("  Python: %s (%s)", platform.python_version(), sys.executable)
    logger.info("  Platform: %s", platform.platform())
    logger.info("  librosa: %s", librosa.__version__)  # type: ignore[attr-defined]

    try:
        import soundfile as sf

        logger.info("  soundfile: %s", sf.__version__)
    except Exception:
        logger.info("  soundfile: NOT AVAILABLE")

    try:
        import audioread

        logger.info("  audioread: %s", audioread.__version__)  # type: ignore[attr-defined]
    except Exception:
        logger.info("  audioread: NOT AVAILABLE")

    logger.info("  numpy: %s", np.__version__)

    try:
        import scipy

        logger.info("  scipy: %s", scipy.__version__)
    except Exception:
        logger.info("  scipy: NOT AVAILABLE")

    try:
        import numba

        logger.info("  numba: %s", numba.__version__)
    except Exception:
        logger.info("  numba: NOT AVAILABLE")

    try:
        import soxr

        logger.info("  soxr: %s", soxr.__version__)
    except Exception:
        logger.info("  soxr: NOT AVAILABLE")

    # Detect which backend librosa will use for a given file
    _log_librosa_backends()
    logger.info("=" * 60)


def _log_librosa_backends() -> None:
    """Log which backends librosa can use and their availability."""
    # soundfile-supported extensions
    try:
        import soundfile as sf

        sf_exts = set(sf.available_formats().keys())
        logger.info(
            "  soundfile available extensions: %s", sorted(e.lower() for e in sf_exts)
        )
    except Exception:
        logger.info("  soundfile: not available")

    # audioread-supported extensions
    try:
        import audioread

        if hasattr(audioread, "available_backends"):
            logger.info(
                "  audioread backends: %s",
                [b.__name__ for b in audioread.available_backends()],
            )
        logger.info("  audioread version: %s", audioread.__version__)  # type: ignore[attr-defined]
    except Exception:
        logger.info("  audioread: not available")

    # librosa's default load function
    try:
        import inspect

        load_source = inspect.getsource(librosa.load)
        # Log a snippet showing the backend logic
        if "soundfile" in load_source:
            logger.info("  librosa.load prefers soundfile, falls back to audioread")
    except Exception:
        pass


def log_ndarray_info(tag: str, arr: np.ndarray) -> None:
    logger.info(
        "  ndarray [%s]: dtype=%s | shape=%s | ndim=%d | nbytes=%d (%.2f MB)"
        " | itemsize=%d | strides=%s",
        tag,
        arr.dtype,
        arr.shape,
        arr.ndim,
        arr.nbytes,
        arr.nbytes / (1024 * 1024),
        arr.itemsize,
        arr.strides,
    )


def log_audio_metadata(
    label: str,
    audio_data: np.ndarray,
    sr: int,
    load_time: float,
) -> None:
    duration = audio_data.shape[-1] / sr
    logger.info(
        "  Audio [%s]: duration=%.2f s | sr=%d | samples=%d"
        " | dtype=%s | nbytes=%d (%.2f MB)"
        " | load_time=%.2f s",
        label,
        duration,
        sr,
        audio_data.shape[-1],
        audio_data.dtype,
        audio_data.nbytes,
        audio_data.nbytes / (1024 * 1024),
        load_time,
    )
    log_ndarray_info(label, audio_data)


def get_memory_delta(before: float, after: float) -> float:
    return after - before
