from __future__ import annotations

import json

import pytest
from app.core.config import settings
from app.infrastructure.storage.demo_media import DemoMediaService
from fastapi import HTTPException


class FakeStorage:
    def __init__(self) -> None:
        self.downloads = 0

    def download(self, path: str) -> bytes:
        self.downloads += 1
        assert path == "demo/manifest.json"
        return json.dumps(valid_manifest()).encode()

    def create_signed_urls(self, paths: list[str], ttl: int) -> list[dict[str, str]]:
        assert ttl == 3600
        return [{"path": path, "signedURL": f"https://media.invalid/{path}?token=private"} for path in paths]


class FakeClient:
    def __init__(self, storage: FakeStorage) -> None:
        self.storage = self
        self._storage = storage

    def from_(self, bucket: str) -> FakeStorage:
        assert bucket == "test-media"
        return self._storage


def valid_manifest() -> dict:
    processed = "2026-07-18T12:00:00Z"
    checksum = f"sha256:{'a' * 64}"

    def asset(name: str, mime: str, duration: float | None = 45) -> dict:
        value = {
            "title": name,
            "objectPath": f"demo/test/{name}.bin",
            "mimeType": mime,
            "sizeBytes": 123,
            "checksum": checksum,
            "processedAt": processed,
            "pipelineVersion": "1.0.0",
        }
        if duration is not None:
            value["duration"] = duration
        return value

    return {
        "id": "mixmind-demo-v1",
        "title": "MixMind real media demonstration",
        "relationship": "trackA + trackB -> transition",
        "assets": {
            "trackA": asset("track-a-preview", "audio/mp4"),
            "trackB": asset("track-b-preview", "audio/mp4"),
            "transition": asset("transition", "audio/mp4", 120),
            "video": asset("clip-720p", "video/mp4", 164),
            "poster": asset("poster", "image/webp", None),
        },
    }


def configured_settings():
    return settings.model_copy(
        update={
            "SUPABASE_URL": "https://project.invalid",
            "SUPABASE_SECRET_KEY": "never-return-this-secret",
            "SUPABASE_STORAGE_BUCKET": "test-media",
            "DEMO_SIGNED_URL_TTL": 3600,
            "DEMO_MANIFEST_CACHE_TTL": 300,
        }
    )


def test_manifest_signs_assets_without_exposing_secret() -> None:
    storage = FakeStorage()
    service = DemoMediaService(configured_settings(), FakeClient(storage))  # type: ignore[arg-type]
    result = service.get_signed_manifest()
    serialized = json.dumps(result)
    assert result["assets"]["video"]["url"].startswith("https://media.invalid/")
    assert "never-return-this-secret" not in serialized
    assert result["expiresAt"] > 0


def test_manifest_uses_private_cache() -> None:
    storage = FakeStorage()
    service = DemoMediaService(configured_settings(), FakeClient(storage))  # type: ignore[arg-type]
    first = service.get_signed_manifest()
    second = service.get_signed_manifest()
    assert first == second
    assert storage.downloads == 1


def test_missing_configuration_is_service_unavailable() -> None:
    config = settings.model_copy(update={"SUPABASE_URL": "", "SUPABASE_SECRET_KEY": ""})
    with pytest.raises(HTTPException) as exc:
        DemoMediaService(config).get_signed_manifest()
    assert exc.value.status_code == 503


def test_manifest_rejects_missing_audio_asset() -> None:
    storage = FakeStorage()
    manifest = valid_manifest()
    del manifest["assets"]["trackB"]
    storage.download = lambda _path: json.dumps(manifest).encode()  # type: ignore[method-assign]
    service = DemoMediaService(configured_settings(), FakeClient(storage))  # type: ignore[arg-type]
    with pytest.raises(HTTPException) as exc:
        service.get_signed_manifest()
    assert exc.value.status_code == 404


def test_manifest_rejects_invalid_checksum() -> None:
    storage = FakeStorage()
    manifest = valid_manifest()
    manifest["assets"]["trackA"]["checksum"] = "invalid"
    storage.download = lambda _path: json.dumps(manifest).encode()  # type: ignore[method-assign]
    service = DemoMediaService(configured_settings(), FakeClient(storage))  # type: ignore[arg-type]
    with pytest.raises(HTTPException) as exc:
        service.get_signed_manifest()
    assert exc.value.status_code == 404
