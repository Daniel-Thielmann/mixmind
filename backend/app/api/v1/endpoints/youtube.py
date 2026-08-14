from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_current_owner_id
from app.api.v1.endpoints.spotify_analysis import _analysis_slot
from app.application.dto.api import UploadAnalysisResponse
from app.application.dto.youtube import YouTubeAnalysisRequest
from app.application.use_cases.analysis.progress import (
    AnalysisProgressEvent,
    AnalysisStage,
)
from app.application.use_cases.analysis.youtube_analysis import youtube_analysis_service
from app.core.exceptions import AppError
from app.infrastructure.youtube.api_client import YouTubeApiClient

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/search")
async def search_youtube(
    q: str = Query(min_length=2, max_length=120),
    page_token: str | None = None,
    _user_id: str = Depends(get_current_owner_id),
) -> dict[str, object]:
    return await YouTubeApiClient().search(q, page_token)


@router.post("/analyze", response_model=UploadAnalysisResponse)
async def analyze_youtube(
    request: YouTubeAnalysisRequest, _user_id: str = Depends(get_current_owner_id)
) -> UploadAnalysisResponse:
    if _analysis_slot.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another analysis is already running.",
        )
    async with _analysis_slot:
        try:
            return await youtube_analysis_service.analyze(request, YouTubeApiClient())
        except AppError:
            raise
        except Exception as exc:
            logger.exception("YouTube analysis failed unexpectedly")
            raise HTTPException(
                status_code=500, detail="YouTube analysis failed unexpectedly."
            ) from exc


@router.post("/analyze/stream", response_class=StreamingResponse)
async def analyze_youtube_stream(
    request: YouTubeAnalysisRequest,
    _user_id: str = Depends(get_current_owner_id),
) -> StreamingResponse:
    if _analysis_slot.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another analysis is already running.",
        )

    async def event_stream() -> AsyncIterator[str]:
        queue: asyncio.Queue[AnalysisProgressEvent | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def report(event: AnalysisProgressEvent) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, event)

        async def run_analysis() -> None:
            try:
                await youtube_analysis_service.analyze(
                    request,
                    YouTubeApiClient(),
                    report,
                )
            except Exception:
                logger.exception("Progressive YouTube analysis failed")
                report(
                    AnalysisProgressEvent(
                        stage=AnalysisStage.FAILED,
                        progress=100,
                        message="YouTube analysis failed. Please try again.",
                    )
                )
            finally:
                queue.put_nowait(None)

        async with _analysis_slot:
            worker = asyncio.create_task(run_analysis())
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield event.model_dump_json() + "\n"
            await worker

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
