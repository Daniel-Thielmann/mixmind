from pathlib import Path
from uuid import uuid4

ALLOWED_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".flac",
}


def get_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def is_allowed_audio(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_EXTENSIONS


def generate_unique_filename(filename: str) -> str:
    extension = get_extension(filename)

    stem = Path(filename).stem

    return f"{uuid4().hex}_{stem}{extension}"
