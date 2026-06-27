from io import BytesIO
from types import SimpleNamespace

from app.services.infrastructure.storage_service import StorageService
from fastapi import UploadFile


def test_save_audio_stores_bytes_in_upload_path(tmp_path, monkeypatch) -> None:
    from app.services.infrastructure import storage_service as storage_module

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
