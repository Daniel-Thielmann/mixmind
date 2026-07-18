from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile


class StoragePort(ABC):
    @abstractmethod
    def save_audio(self, file: UploadFile) -> Path: ...
