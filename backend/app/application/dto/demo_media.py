from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

REQUIRED_ASSETS = {"trackA", "trackB", "transition", "video", "poster"}


class DemoMediaAsset(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1)
    object_path: str = Field(alias="objectPath", min_length=1)
    mime_type: str = Field(alias="mimeType", pattern=r"^(audio|video|image)/")
    size_bytes: int = Field(alias="sizeBytes", gt=0)
    duration: float | None = Field(default=None, gt=0)
    original_start: float | None = Field(default=None, alias="originalStart", ge=0)
    original_end: float | None = Field(default=None, alias="originalEnd", gt=0)
    checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    processed_at: datetime = Field(alias="processedAt")
    pipeline_version: str = Field(alias="pipelineVersion", min_length=1)
    url: HttpUrl | None = None

    @model_validator(mode="after")
    def validate_interval(self) -> DemoMediaAsset:
        if self.original_start is not None and self.original_end is not None:
            if self.original_end <= self.original_start:
                raise ValueError("originalEnd must be greater than originalStart")
        return self


class DemoMediaManifest(BaseModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    relationship: str = Field(min_length=1)
    assets: dict[str, DemoMediaAsset]
    expires_at: int | None = Field(default=None, alias="expiresAt", gt=0)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_required_assets(self) -> DemoMediaManifest:
        missing = REQUIRED_ASSETS - set(self.assets)
        if missing:
            raise ValueError(f"missing required demo assets: {', '.join(sorted(missing))}")
        expected = {
            "trackA": "audio/",
            "trackB": "audio/",
            "transition": "audio/",
            "video": "video/",
            "poster": "image/",
        }
        for name, prefix in expected.items():
            if not self.assets[name].mime_type.startswith(prefix):
                raise ValueError(f"{name} must use a {prefix} MIME type")
        return self
