import shutil
from pathlib import Path
from typing import Protocol

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidAudioFileException
from app.domain.value_objects.file_utils import (
    generate_unique_filename,
    is_allowed_audio,
)
from app.infrastructure.storage.supabase_storage import build_supabase_storage


class RemoteStorage(Protocol):
    @property
    def bucket(self) -> str: ...

    def health(self) -> dict[str, object]: ...

    def upload_file(self, local_path: Path, object_path: str) -> str | None: ...


class StorageService:
    """
    Responsible for storing uploaded audio files.
    """

    def __init__(self, remote: RemoteStorage | None = None) -> None:
        self._remote = remote if remote is not None else build_supabase_storage()

    def save_audio(self, file: UploadFile) -> Path:
        # Ensure the uploaded file has a filename
        if not file.filename:
            raise InvalidAudioFileException("<unknown>")

        # filename is now guaranteed to be a non-empty string
        filename_str: str = file.filename

        if not is_allowed_audio(filename_str):
            raise InvalidAudioFileException(filename_str)

        filename = generate_unique_filename(filename_str)

        destination = settings.upload_path / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

            file.file.close()

        if self._remote is not None:
            self._remote.upload_file(destination, f"uploads/{filename}")

        return destination

    def storage_health(self) -> dict[str, object]:
        if self._remote is None:
            return {
                "configured": False,
                "connected": False,
                "bucket": None,
                "public": False,
            }
        return self._remote.health()

    def upload_artifact(self, local_path: Path, object_path: str) -> str | None:
        if self._remote is None:
            return None
        return self._remote.upload_file(local_path, object_path)

    def save_video(self, file: UploadFile) -> tuple[Path, str | None]:
        if not file.filename:
            raise InvalidAudioFileException("<unknown>")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in {".mp4", ".webm", ".mov", ".m4v"}:
            raise InvalidAudioFileException(file.filename)

        filename = generate_unique_filename(file.filename)
        video_dir = settings.upload_path / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        destination = video_dir / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            file.file.close()

        url = self.upload_artifact(destination, f"videos/{filename}")
        return destination, url


storage_service = StorageService()
