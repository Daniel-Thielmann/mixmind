from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum

from pydantic import BaseModel, Field, JsonValue


class AnalysisStage(StrEnum):
    ACQUIRING_TRACKS = "acquiring_tracks"
    TRACKS_ACQUIRED = "tracks_acquired"
    STARTED = "started"
    FILES_SAVED = "files_saved"
    TRACK_A_ANALYZED = "track_a_analyzed"
    TRACK_B_ANALYZED = "track_b_analyzed"
    COMPATIBILITY_COMPUTED = "compatibility_computed"
    AI_RECOMMENDATION_STARTED = "ai_recommendation_started"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisProgressEvent(BaseModel):
    """One observable milestone emitted by the sequential analysis pipeline."""

    stage: AnalysisStage
    progress: int = Field(ge=0, le=100)
    message: str
    analysis_id: str | None = None
    data: JsonValue | None = None


AnalysisProgressCallback = Callable[[AnalysisProgressEvent], None]
