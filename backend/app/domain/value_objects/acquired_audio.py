from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class AcquiredAudio:
    local_path: Path
    mime_type: str
    provider: str
    temporary: bool = True
    size_bytes: int = 0
    checksum_sha256: str | None = None
    original_filename: str | None = None
