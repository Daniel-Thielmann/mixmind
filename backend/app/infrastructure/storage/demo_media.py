from __future__ import annotations

import json
import time
from copy import deepcopy
from typing import TYPE_CHECKING, Any

from app.core.config import Settings, settings
from fastapi import HTTPException, status
if TYPE_CHECKING:
    from supabase import Client

MANIFEST_PATH = "demo/manifest.json"


class DemoMediaService:
    """Reads the private demo manifest and signs its stable object paths."""

    def __init__(self, config: Settings = settings, client: Client | None = None) -> None:
        self.config = config
        self._client = client
        self._cached: tuple[float, dict[str, Any]] | None = None

    def _storage(self) -> Any:
        if not self.config.SUPABASE_URL or not self.config.SUPABASE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Demonstration media is not configured.",
            )
        if self._client is None:
            try:
                from supabase import create_client
            except ImportError as exc:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Demonstration storage dependency is unavailable.",
                ) from exc
            client = create_client(
                self.config.SUPABASE_URL, self.config.SUPABASE_SECRET_KEY
            )
        else:
            client = self._client
        return client.storage.from_(self.config.SUPABASE_STORAGE_BUCKET)

    def get_signed_manifest(self) -> dict[str, Any]:
        now = time.time()
        if self._cached and now - self._cached[0] < self.config.DEMO_MANIFEST_CACHE_TTL:
            return deepcopy(self._cached[1])

        storage = self._storage()
        try:
            raw = storage.download(MANIFEST_PATH)
            manifest = json.loads(raw.decode("utf-8"))
            assets = manifest.get("assets", {})
            paths = [asset["objectPath"] for asset in assets.values()]
            signed = storage.create_signed_urls(paths, self.config.DEMO_SIGNED_URL_TTL)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Demonstration media is unavailable.",
            ) from exc

        urls = {item["path"]: item.get("signedURL") or item.get("signedUrl") for item in signed}
        for asset in assets.values():
            asset["url"] = urls.get(asset["objectPath"])
        manifest["expiresAt"] = int(now) + self.config.DEMO_SIGNED_URL_TTL
        self._cached = (now, manifest)
        return deepcopy(manifest)


demo_media_service = DemoMediaService()
