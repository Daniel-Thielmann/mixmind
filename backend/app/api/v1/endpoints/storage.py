from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.infrastructure.storage.storage_service import storage_service

router = APIRouter()


@router.get("/health", summary="Supabase Storage health check")
def storage_health() -> dict[str, object]:
    return storage_service.storage_health()


@router.post("/videos", summary="Upload a video to Supabase Storage")
def upload_video(video: UploadFile = File(...)) -> dict[str, object]:
    path, url = storage_service.save_video(video)
    return {
        "status": "success",
        "filename": path.name,
        "object_path": f"videos/{path.name}",
        "url": url,
    }
