from fastapi import APIRouter, File, UploadFile

from app.schemas.response import UploadedTrack, UploadResponse
from app.services.storage_service import storage_service

router = APIRouter()


@router.get("/")
async def analysis_status():
    """
    Health check do módulo de análise.
    """
    return {
        "service": "Analysis Service",
        "status": "available",
    }


@router.post(
    "/analyze",
    response_model=UploadResponse,
    summary="Upload and analyze two tracks",
)
async def analyze_tracks(
    track_a: UploadFile = File(...),
    track_b: UploadFile = File(...),
):
    path_a = storage_service.save(track_a)
    path_b = storage_service.save(track_b)

    track_a_name = track_a.filename or ""
    track_b_name = track_b.filename or ""

    return UploadResponse(
        status="success",
        message="Tracks uploaded successfully",
        track_a=UploadedTrack(
            filename=track_a_name,
            stored_as=path_a.name,
            status="uploaded",
        ),
        track_b=UploadedTrack(
            filename=track_b_name,
            stored_as=path_b.name,
            status="uploaded",
        ),
    )
