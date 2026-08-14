from __future__ import annotations

import asyncio

from app.application.dto.api import UploadAnalysisResponse
from app.application.dto.youtube import YouTubeAnalysisRequest
from app.application.use_cases.analysis.spotify_analysis.dto import (
    SpotifyAnalysisRequest,
)
from app.application.use_cases.analysis.spotify_analysis.service import (
    SpotifyAnalysisService,
)
from app.infrastructure.youtube.api_client import YouTubeApiClient
from app.infrastructure.youtube.rapidapi_downloader import RapidApiYouTubeDownloader


class YouTubeAnalysisService:
    def __init__(self) -> None:
        self._analysis = SpotifyAnalysisService(downloader=RapidApiYouTubeDownloader())

    async def analyze(
        self, request: YouTubeAnalysisRequest, client: YouTubeApiClient
    ) -> UploadAnalysisResponse:
        video_a = request.video_id("track_a")
        video_b = request.video_id("track_b")
        metadata_a, metadata_b = await asyncio.gather(
            client.metadata(video_a), client.metadata(video_b)
        )

        class MetadataClient:
            async def get_track_metadata(self, track_id: str):
                return metadata_a if track_id == video_a else metadata_b

        adapted = SpotifyAnalysisRequest.model_validate(
            {
                "tracks": [
                    {"position": "track_a", "spotify_track_id": video_a},
                    {"position": "track_b", "spotify_track_id": video_b},
                ]
            }
        )
        return await self._analysis.analyze(adapted, MetadataClient())  # type: ignore[arg-type]


youtube_analysis_service = YouTubeAnalysisService()
