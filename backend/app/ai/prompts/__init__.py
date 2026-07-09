"""Prompt construction for the DJ assistant."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal, TypedDict

from app.schemas.api import UploadAnalysisResponse
from app.services.mix_scoring_service import MixScore


class LLMMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


_PROMPT_DIR = Path(__file__).resolve().parent
_PROMPT_CACHE: str | None = None


def load_prompt() -> str:
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        path = _PROMPT_DIR / "dj_system_prompt.md"
        _PROMPT_CACHE = path.read_text(encoding="utf-8")
    return _PROMPT_CACHE


def build_llm_payload(
    response: UploadAnalysisResponse,
    mix_score: MixScore | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "analysis_id": response.analysis_id,
        "track_a": {
            "filename": response.track_a.filename,
            "bpm": response.track_a.bpm,
            "energy": response.track_a.energy,
        },
        "track_b": {
            "filename": response.track_b.filename,
            "bpm": response.track_b.bpm,
            "energy": response.track_b.energy,
        },
        "compatibility": {
            "compatibility_score": response.compatibility.compatibility_score,
            "tempo_difference": response.compatibility.tempo_difference,
            "energy_difference": response.compatibility.energy_difference,
            "overall_rating": response.compatibility.overall_rating,
        },
    }

    if mix_score is not None:
        payload["mix_scoring"] = asdict(mix_score)

    return payload


def build_dj_messages(payload: dict[str, Any]) -> list[LLMMessage]:
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
