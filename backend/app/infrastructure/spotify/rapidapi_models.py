from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RapidApiDownloadData(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    download_link: str | None = Field(default=None, alias="downloadLink")
    id: str | None = None
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    cover: str | None = None


class RapidApiDownloadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    success: bool
    data: RapidApiDownloadData | None = None
    message: str | None = None
    generated_time_stamp: int | None = Field(default=None, alias="generatedTimeStamp")
