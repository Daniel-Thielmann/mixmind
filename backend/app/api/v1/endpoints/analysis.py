from fastapi import APIRouter, File, UploadFile

from app.application.dto.api import UploadAnalysisResponse
from app.application.use_cases.analysis.analyze_track import analysis_service

router = APIRouter()


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
) -> UploadAnalysisResponse:
    return analysis_service.analyze(track_a, track_b)
