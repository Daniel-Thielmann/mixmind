"""Model Registry — manages model lifecycle, validation, and cooldown."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

_INVALID_MODEL_MESSAGE = "is not a valid model ID"
_COOLDOWN_DURATION = 600


@dataclass
class ModelInfo:
    name: str
    valid: bool = True
    cooldown_until: float = 0.0
    success_count: int = 0
    error_count: int = 0
    total_latency: float = 0.0


class ModelRegistry:
    def __init__(self, models: list[str] | None = None) -> None:
        self._models: dict[str, ModelInfo] = {}
        if models:
            self.register_models(models)

    def register_models(self, models: list[str]) -> None:
        for model in models:
            if model not in self._models:
                self._models[model] = ModelInfo(name=model)

    def get_available_models(self) -> list[str]:
        now = time.monotonic()
        available = [
            name
            for name, info in self._models.items()
            if info.valid and info.cooldown_until <= now
        ]
        available.sort(
            key=lambda m: (
                -(
                    self._models[m].success_count
                    / max(
                        1, self._models[m].success_count + self._models[m].error_count
                    )
                ),
                self._models[m].total_latency / max(1, self._models[m].success_count),
                self._models[m].error_count,
            )
        )
        return available

    def mark_invalid(self, model: str) -> None:
        info = self._models.get(model)
        if info is not None and info.valid:
            info.valid = False
            logger.warning(
                "Model %s marked as invalid — removed from fallback cycle", model
            )

    def mark_cooldown(self, model: str, duration: int = _COOLDOWN_DURATION) -> None:
        info = self._models.get(model)
        if info is not None:
            info.cooldown_until = time.monotonic() + duration
            logger.info("Model %s entered cooldown (%d min)", model, duration // 60)

    def record_success(self, model: str, latency: float) -> None:
        info = self._models.get(model)
        if info is not None:
            info.success_count += 1
            info.total_latency += latency

    def record_error(self, model: str) -> None:
        info = self._models.get(model)
        if info is not None:
            info.error_count += 1

    def get_valid_models(self) -> list[str]:
        return [name for name, info in self._models.items() if info.valid]

    def get_invalid_models(self) -> list[str]:
        return [name for name, info in self._models.items() if not info.valid]

    def get_cooldown_models(self) -> list[str]:
        now = time.monotonic()
        return [
            name for name, info in self._models.items() if info.cooldown_until > now
        ]

    def is_valid(self, model: str) -> bool:
        info = self._models.get(model)
        return info is not None and info.valid

    def health(self) -> dict[str, Any]:
        return {
            "available_models": self.get_available_models(),
            "cooldown_models": self.get_cooldown_models(),
            "invalid_models": self.get_invalid_models(),
        }

    def check_invalid_response(self, model: str, status_code: int, body: str) -> bool:
        if status_code == 400 and _INVALID_MODEL_MESSAGE in body:
            self.mark_invalid(model)
            return True
        return False
