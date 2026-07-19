import asyncio

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.api.dependencies import AnalysisOwnerId, AnalysisTrackRepositoryDependency
from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track import analysis_service
from app.application.use_cases.analysis.persist_tracks import PersistAnalyzedTracks

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
