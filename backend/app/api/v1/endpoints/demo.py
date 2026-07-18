from __future__ import annotations

from app.application.dto.demo_media import DemoMediaManifest
from app.infrastructure.storage.demo_media import demo_media_service
from fastapi import APIRouter

router = APIRouter()


@router.get("/manifest", response_model=DemoMediaManifest, response_model_by_alias=True)
def get_demo_manifest() -> DemoMediaManifest:
    return DemoMediaManifest.model_validate(demo_media_service.get_signed_manifest())
