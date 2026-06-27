from fastapi import APIRouter, File, UploadFile

from app.schemas.api import UploadAnalysisResponse
from app.services.analysis_service import analysis_service

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
    return analysis_service.upload_tracks(track_a, track_b)
