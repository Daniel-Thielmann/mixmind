from __future__ import annotations

from typing import Any

from app.infrastructure.storage.demo_media import demo_media_service
from fastapi import APIRouter

router = APIRouter()


@router.get("/manifest", response_model=dict[str, Any])
def get_demo_manifest() -> dict[str, Any]:
    return demo_media_service.get_signed_manifest()
