from pathlib import Path
import shutil

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import InvalidAudioFileException
from app.utils.file_utils import (
    generate_unique_filename,
    is_allowed_audio,
)


class StorageService:
    """
    Responsible for storing uploaded audio files.
    """

    def save(self, file: UploadFile) -> Path:
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

            return destination


storage_service = StorageService()
