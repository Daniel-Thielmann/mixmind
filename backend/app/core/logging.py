from __future__ import annotations

import logging
import sys


class LoggingConfig:
    log_level: str = "INFO"
    json_format: bool = False
    app_name: str = "mixmind"


JSON_LOG_FORMAT: str = (
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
    '"name": "%(name)s", "message": "%(message)s"}'
)

CONSOLE_LOG_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    *,
    log_level: str = "INFO",
    json_format: bool = False,
    app_name: str = "mixmind",
) -> None:
    log_format = JSON_LOG_FORMAT if json_format else CONSOLE_LOG_FORMAT

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=DATE_FORMAT,
        handlers=handlers,
        force=True,
    )

    _silence_noisy_libraries()

    logger = logging.getLogger(app_name)
    logger.info(
        "Logging configured | level=%s | json_format=%s",
        log_level,
        json_format,
    )


def _silence_noisy_libraries() -> None:
    for lib in ("httpx", "matplotlib", "urllib3", "asyncio"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
