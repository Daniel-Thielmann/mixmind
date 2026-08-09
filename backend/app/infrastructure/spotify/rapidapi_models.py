from __future__ import annotations

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class RapidApiDownloadData(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    download_link: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "downloadLink",
            "downloadUrl",
            "download_url",
            "url",
            "link",
        ),
    )
    id: str | None = None
    title: str | None = None
    artist: str | None = None
    album: str | None = None
    cover: str | None = None


class RapidApiDownloadResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    success: bool | str | int = Field(
        default=True,
        validation_alias=AliasChoices("success", "status"),
    )
    data: RapidApiDownloadData | str | None = Field(
        default=None,
        validation_alias=AliasChoices("data", "result"),
    )
    download_link: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "downloadLink",
            "downloadUrl",
            "download_url",
            "url",
            "link",
        ),
    )
    message: str | None = Field(
        default=None,
        validation_alias=AliasChoices("message", "error"),
    )
    generated_time_stamp: int | None = Field(default=None, alias="generatedTimeStamp")
