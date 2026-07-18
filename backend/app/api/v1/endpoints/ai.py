"""AI health and diagnostics endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.infrastructure.llm.agent import dj_agent

router = APIRouter()


@router.get(
    "/health",
    summary="AI infrastructure health check",
)
async def ai_health() -> dict[str, object]:
    llm_manager = dj_agent._llm_manager
    health_data = llm_manager.health()
    stats_data = llm_manager.stats()
    return {
        "status": "ok",
        **health_data,
        "stats": stats_data,
    }
