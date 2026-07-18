from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from supabase import Client, create_client

from app.core.config import Settings, settings
from app.core.exceptions import InfrastructureError


class SupabaseStorage:
    def __init__(
        self,
        url: str,
        secret_key: str,
        bucket: str,
        *,
        public: bool = False,
        signed_url_ttl: int = 3600,
    ) -> None:
        self._client: Client = create_client(url, secret_key)
        self._bucket = bucket
        self._public = public
        self._signed_url_ttl = signed_url_ttl

    @property
    def bucket(self) -> str:
        return self._bucket

    def health(self) -> dict[str, object]:
        try:
            bucket = self._client.storage.get_bucket(self._bucket)
        except Exception as exc:
            raise InfrastructureError(
                f"Unable to connect to Supabase Storage bucket '{self._bucket}'"
            ) from exc

        return {
            "configured": True,
            "connected": True,
            "bucket": self._bucket,
            "public": bool(getattr(bucket, "public", self._public)),
        }

    def upload_file(self, local_path: Path, object_path: str) -> str | None:
        content_type = mimetypes.guess_type(local_path.name)[0]
        options: dict[str, Any] = {"upsert": "false"}
        if content_type:
            options["content-type"] = content_type

        try:
            with local_path.open("rb") as source:
                self._client.storage.from_(self._bucket).upload(
                    path=object_path,
                    file=source,
                    file_options=options,
                )
        except Exception as exc:
            raise InfrastructureError(
                f"Unable to upload '{object_path}' to Supabase Storage"
            ) from exc

        bucket = self._client.storage.from_(self._bucket)
        if self._public:
            return bucket.get_public_url(object_path)

        signed = bucket.create_signed_url(object_path, self._signed_url_ttl)
        if isinstance(signed, dict):
            return signed.get("signedURL") or signed.get("signedUrl")
        return getattr(signed, "signed_url", None)


def build_supabase_storage(
    app_settings: Settings = settings,
) -> SupabaseStorage | None:
    if not app_settings.is_supabase_storage_configured:
        return None
    return SupabaseStorage(
        url=app_settings.SUPABASE_URL,
        secret_key=app_settings.SUPABASE_SECRET_KEY,
        bucket=app_settings.SUPABASE_STORAGE_BUCKET,
        public=app_settings.SUPABASE_STORAGE_PUBLIC,
        signed_url_ttl=app_settings.SUPABASE_SIGNED_URL_TTL,
    )
