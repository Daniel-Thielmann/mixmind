from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RapidApiDownloadData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    download_link: str | None = Field(default=None, alias="downloadLink")
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    cover: str | None = None


class RapidApiDownloadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool
    data: RapidApiDownloadData | None = None
    message: str | None = None
