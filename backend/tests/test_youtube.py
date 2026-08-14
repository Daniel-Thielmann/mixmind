from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
from pydantic import ValidationError

from app.application.dto.youtube import YouTubeAnalysisRequest
from app.infrastructure.youtube.api_client import _duration_ms
from app.infrastructure.youtube.rapidapi_downloader import _extract_url


def test_youtube_request_requires_distinct_valid_video_ids() -> None:
    request = YouTubeAnalysisRequest(
        tracks=[
            {"position": "track_a", "youtube_video_id": "abcdefghijk"},
            {"position": "track_b", "youtube_video_id": "12345678901"},
        ]
    )
    assert request.video_id("track_a") == "abcdefghijk"
    with pytest.raises(ValidationError):
        YouTubeAnalysisRequest(
            tracks=[
                {"position": "track_a", "youtube_video_id": "bad"},
                {"position": "track_b", "youtube_video_id": "bad"},
            ]
        )


def test_iso_duration_conversion() -> None:
    assert _duration_ms("PT1H2M3S") == 3_723_000


@pytest.mark.parametrize(
    "payload, expected",
    [
        ("https://cdn.example/audio.mp3", "https://cdn.example/audio.mp3"),
        ({"download_url": "https://cdn.example/file"}, "https://cdn.example/file"),
    ],
)
def test_provider_response_url_shapes(payload, expected) -> None:
    response = MagicMock(spec=httpx.Response)
    response.text = payload if isinstance(payload, str) else ""
    response.json.return_value = payload
    assert _extract_url(response) == expected
