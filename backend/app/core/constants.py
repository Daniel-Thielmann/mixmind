from __future__ import annotations

from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent.parent
BACKEND_ROOT: Path = PROJECT_ROOT

APP_NAME: str = "MixMind AI"
APP_VERSION: str = "1.0.0"
API_V1_PREFIX: str = "/api/v1"

ALLOWED_AUDIO_EXTENSIONS: frozenset[str] = frozenset({".mp3", ".wav", ".flac"})
MAX_UPLOAD_SIZE_MB: int = 100
MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

DEFAULT_ENCODING: str = "utf-8"
DEFAULT_CACHE_TTL: int = 1800
