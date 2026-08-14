import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.dependencies import AnalysisOwnerId, AnalysisTrackRepositoryDependency
from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track import analysis_service
from app.application.use_cases.analysis.persist_tracks import PersistAnalyzedTracks
from app.application.use_cases.analysis.progress import (
    AnalysisProgressEvent,
    AnalysisStage,
)

router = APIRouter()
_analysis_slot = asyncio.Semaphore(1)


@router.get("/")
async def analysis_status() -> dict[str, str]:
    return {
        "service": "Analysis Service",
        "status": "available",
    }


@router.post(
    "/analyze",
    response_model=UploadAnalysisResponse,
    summary="Upload and analyze two tracks",
)
async def analyze_tracks(
    track_a: UploadFile = File(...),
    track_b: UploadFile = File(...),
    repository: AnalysisTrackRepositoryDependency = None,
    owner_id: AnalysisOwnerId = "anonymous",
) -> UploadAnalysisResponse:
    if _analysis_slot.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another analysis is already running. Please try again shortly.",
        )

    async with _analysis_slot:
        response = await asyncio.to_thread(analysis_service.analyze, track_a, track_b)
    if repository is not None and owner_id != "anonymous":
        PersistAnalyzedTracks(repository).execute(response.track_a, response.track_b)
    return response


@router.post(
    "/analyze/stream",
    summary="Upload and analyze two tracks with progressive events",
    response_class=StreamingResponse,
)
async def analyze_tracks_stream(
    track_a: UploadFile = File(...),
    track_b: UploadFile = File(...),
    repository: AnalysisTrackRepositoryDependency = None,
    owner_id: AnalysisOwnerId = "anonymous",
) -> StreamingResponse:
    """Stream newline-delimited JSON milestones from the sequential pipeline."""
    if _analysis_slot.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Another analysis is already running. Please try again shortly.",
        )

    async def event_stream() -> AsyncIterator[str]:
        queue: asyncio.Queue[AnalysisProgressEvent | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def report(event: AnalysisProgressEvent) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, event)

        def run_analysis() -> UploadAnalysisResponse | None:
            try:
                return analysis_service.analyze(
                    track_a,
                    track_b,
                    on_progress=report,
                )
            except Exception:
                report(
                    AnalysisProgressEvent(
                        stage=AnalysisStage.FAILED,
                        progress=100,
                        message="Analysis failed. Please try again.",
                    )
                )
                return None
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        async with _analysis_slot:
            worker = asyncio.create_task(asyncio.to_thread(run_analysis))
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield event.model_dump_json() + "\n"
            response = await worker
            if (
                response is not None
                and repository is not None
                and owner_id != "anonymous"
            ):
                PersistAnalyzedTracks(repository).execute(
                    response.track_a,
                    response.track_b,
                )

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
