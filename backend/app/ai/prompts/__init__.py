"""Prompt construction for the DJ assistant."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal, TypedDict

from app.schemas.api import UploadAnalysisResponse
from app.services.mix_scoring_service import MixScore


class LLMMessage(TypedDict):
    """OpenAI-style chat message payload."""

    role: Literal["system", "user", "assistant"]
    content: str


_PROMPT_DIR = Path(__file__).resolve().parent
_PROMPT_CACHE: str | None = None


def load_prompt() -> str:
    """Read the DJ system prompt from the external markdown file."""
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        path = _PROMPT_DIR / "dj_system_prompt.md"
        _PROMPT_CACHE = path.read_text(encoding="utf-8")
    return _PROMPT_CACHE


def build_llm_payload(
    response: UploadAnalysisResponse,
    mix_score: MixScore | None = None,
) -> dict[str, Any]:
    """Build the structured data dict sent to the DJ assistant.

    Uses the exact field names from the backend schemas so the LLM
    receives the same vocabulary used throughout the application.
    """

    payload: dict[str, Any] = {
        "analysis_id": response.analysis_id,
        "status": response.status,
        "message": response.message,
        "track_a": {
            "filename": response.track_a.filename,
            "bpm": response.track_a.bpm,
            "energy": response.track_a.energy,
            "duration": response.track_a.duration,
            "sample_rate": response.track_a.sample_rate,
        },
        "track_b": {
            "filename": response.track_b.filename,
            "bpm": response.track_b.bpm,
            "energy": response.track_b.energy,
            "duration": response.track_b.duration,
            "sample_rate": response.track_b.sample_rate,
        },
        "compatibility": {
            "compatibility_score": response.compatibility.compatibility_score,
            "tempo_difference": response.compatibility.tempo_difference,
            "energy_difference": response.compatibility.energy_difference,
            "tempo_match": response.compatibility.tempo_match,
            "energy_match": response.compatibility.energy_match,
            "overall_rating": response.compatibility.overall_rating,
        },
    }

    if mix_score is not None:
        payload["mix_scoring"] = asdict(mix_score)

    return payload


def build_dj_messages(payload: dict[str, Any]) -> list[LLMMessage]:
    """Build the chat messages used to query the DJ assistant."""

    return [
        {
            "role": "system",
            "content": load_prompt(),
        },
        {
            "role": "user",
            "content": json.dumps(
                payload,
                indent=2,
                ensure_ascii=False,
            ),
        },
    ]
