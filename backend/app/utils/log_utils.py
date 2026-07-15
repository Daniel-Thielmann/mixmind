import logging

import psutil

logger = logging.getLogger(__name__)


def get_memory_mb() -> float:
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def log_memory(tag: str) -> None:
    mem = get_memory_mb()
    logger.info("Memory [%s]: %.2f MB", tag, mem)
