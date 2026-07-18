from io import BytesIO
from types import SimpleNamespace

from fastapi import UploadFile

from app.infrastructure.storage.storage_service import StorageService


class FakeRemoteStorage:
    bucket = "test-bucket"

    def __init__(self) -> None:
        self.uploaded: list[tuple[bytes, str]] = []

    def health(self) -> dict[str, object]:
        return {"configured": True, "connected": True, "bucket": self.bucket}

    def upload_file(self, local_path, object_path: str) -> str | None:
        self.uploaded.append((local_path.read_bytes(), object_path))
        return None


def test_save_audio_stores_bytes_in_upload_path(tmp_path, monkeypatch) -> None:
    from app.infrastructure.storage import storage_service as storage_module

    monkeypatch.setattr(
        storage_module,
        "settings",
        SimpleNamespace(upload_path=tmp_path),
    )

    service = StorageService()
    uploaded_file = UploadFile(filename="track.mp3", file=BytesIO(b"abc123"))

    stored_path = service.save_audio(uploaded_file)

    assert stored_path.exists()
    assert stored_path.suffix == ".mp3"
    assert stored_path.read_bytes() == b"abc123"


def test_save_audio_mirrors_file_to_remote_storage(tmp_path, monkeypatch) -> None:
    from app.infrastructure.storage import storage_service as storage_module

    monkeypatch.setattr(
        storage_module,
        "settings",
        SimpleNamespace(upload_path=tmp_path),
    )
    remote = FakeRemoteStorage()
    service = StorageService(remote=remote)
    uploaded_file = UploadFile(filename="track.mp3", file=BytesIO(b"abc123"))

    stored_path = service.save_audio(uploaded_file)

    assert stored_path.exists()
    assert remote.uploaded == [(b"abc123", f"uploads/{stored_path.name}")]


def test_save_video_mirrors_file_to_remote_storage(tmp_path, monkeypatch) -> None:
    from app.infrastructure.storage import storage_service as storage_module

    monkeypatch.setattr(
        storage_module,
        "settings",
        SimpleNamespace(upload_path=tmp_path),
    )
    remote = FakeRemoteStorage()
    service = StorageService(remote=remote)
    uploaded_file = UploadFile(filename="demo.mp4", file=BytesIO(b"video"))

    stored_path, url = service.save_video(uploaded_file)

    assert stored_path.exists()
    assert url is None
    assert remote.uploaded == [(b"video", f"videos/{stored_path.name}")]
