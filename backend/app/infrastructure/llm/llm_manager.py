"""Orchestrates model fallback, retry, JSON repair, and schema validation."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings
from app.infrastructure.llm.cache import RecommendationCache, recommendation_cache
from app.infrastructure.llm.client import LLMClient, OpenAICompatibleLLMClient
from app.infrastructure.llm.exceptions import (
    LLMAllModelsFailed,
    LLMHTTPError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMValidationError,
)
from app.infrastructure.llm.metrics import LLMMetricsCollector, llm_metrics
from app.infrastructure.llm.model_registry import ModelRegistry
from json_repair import repair_json

logger = logging.getLogger(__name__)


_FIELD_DEFAULTS: dict[str, Any] = {
    "summary": "No summary provided.",
    "mix_direction": "No direction provided.",
    "club_tip": "",
    "professional_notes": "",
    "confidence": 50,
}

_RICH_FIELDS: set[str] = set()


@dataclass
class LLMMetrics:
    request_id: str = ""
    model_attempts: list[str] = field(default_factory=list)
    total_attempts: int = 0
    repair_count: int = 0
    parse_time: float = 0.0
    total_time: float = 0.0
    success: bool = False
    final_model: str = ""
    fallback: bool = False
    fallback_level: int = 0
    fallback_reason: str = ""
    filled_fields: list[str] = field(default_factory=list)
    response_size: int = 0
    finish_reason: str = ""
    validation_passed: bool = False


class LLMManager:
    def __init__(
        self,
        models: list[str],
        base_url: str,
        api_key: str,
        *,
        client: LLMClient | None = None,
        request_id: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        backoff_base: float | None = None,
        registry: ModelRegistry | None = None,
        metrics_collector: LLMMetricsCollector | None = None,
        cache: RecommendationCache | None = None,
    ) -> None:
        self._injected_client = client
        self._request_id = request_id or uuid.uuid4().hex[:8]
        self._timeout = timeout if timeout is not None else settings.LLM_TIMEOUT
        self._max_retries = (
            max_retries if max_retries is not None else settings.LLM_MAX_RETRIES
        )
        self._backoff_base = (
            backoff_base
            if backoff_base is not None
            else settings.LLM_RETRY_BACKOFF_BASE
        )

        self._registry = registry or ModelRegistry(models)
        self._metrics_collector = metrics_collector or llm_metrics
        self._cache = cache or recommendation_cache

        self._base_url = base_url
        self._api_key = api_key
        self._models = models

    def generate(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        validator: Callable[[dict[str, Any]], bool] | None = None,
    ) -> tuple[dict[str, Any], str, int]:
        metrics = LLMMetrics(request_id=self._request_id)
        start = time.monotonic()

        last_error: Exception | None = None

        models_to_try = self._registry.get_available_models()
        if not models_to_try:
            models_to_try = list(self._models)

        for model_idx, model in enumerate(models_to_try):
            metrics.fallback_level = model_idx

            if model_idx > 0 and self._injected_client is not None:
                logger.info(
                    "[%s] Skipping fallback model %s (injected client in use)",
                    self._request_id,
                    model,
                )
                break

            if not self._registry.is_valid(model):
                logger.info(
                    "[%s] Skipping invalid model %s",
                    self._request_id,
                    model,
                )
                continue

            client = self._resolve_client(model_idx, model)

            logger.info(
                "Trying model: %s",
                model,
            )

            # --- Primary call ---
            metrics.total_attempts += 1
            metrics.model_attempts.append(f"{model}#1")
            self._log_request_start(model, 0)

            raw, retryable = self._try_call(
                client, model, messages, temperature, max_tokens, metrics
            )

            if raw is None:
                last_error = self._last_call_error
                category = self._categorize_error(last_error)

                if self._is_immediate_switch(category):
                    reason = self._format_error_reason(last_error, category)
                    logger.warning(
                        "Model failed: %s\n"
                        "Reason: %s\n"
                        "Action: Switching immediately to next model.",
                        model,
                        reason,
                    )
                    metrics.fallback_reason = reason
                    continue

                if retryable:
                    delay = self._backoff(0)
                    reason = self._format_error_reason(last_error, category)
                    logger.warning(
                        "Model failed: %s\nReason: %s\nAction: Retry 1/1 (wait %.1fs)",
                        model,
                        reason,
                        delay,
                    )
                    time.sleep(delay)

                    # --- Retry call ---
                    metrics.total_attempts += 1
                    metrics.model_attempts.append(f"{model}#2")
                    self._log_request_start(model, 1)

                    raw, retryable = self._try_call(
                        client, model, messages, temperature, max_tokens, metrics
                    )

                    if raw is None:
                        last_error = self._last_call_error
                        category = self._categorize_error(last_error)
                        reason = self._format_error_reason(last_error, category)
                        logger.warning(
                            "Model failed: %s\n"
                            "Reason: %s\n"
                            "Action: Retry failed. Switching to next model.",
                            model,
                            reason,
                        )
                        metrics.fallback_reason = reason
                        continue
                else:
                    reason = self._format_error_reason(last_error, category)
                    logger.warning(
                        "Model failed: %s\n"
                        "Reason: %s\n"
                        "Action: Not retryable. Switching to next model.",
                        model,
                        reason,
                    )
                    metrics.fallback_reason = reason
                    continue

            self._maybe_log_raw_response(model, raw)

            # --- Parse JSON ---
            parsed = self._repair_and_parse(raw)
            if parsed is None:
                self._metrics_collector.record_json_error()
                self._log_raw_parse_error(model, raw)

                logger.warning(
                    "Model failed: %s\nReason: Invalid JSON\nAction: Retry 1/1",
                    model,
                )

                metrics.total_attempts += 1
                metrics.model_attempts.append(f"{model}#json-retry")
                raw, retryable = self._try_call(
                    client, model, messages, temperature, max_tokens, metrics
                )

                if raw is not None:
                    self._maybe_log_raw_response(model, raw)
                    parsed = self._repair_and_parse(raw)

                if parsed is None:
                    logger.warning(
                        "Model failed: %s\n"
                        "Reason: Invalid JSON\n"
                        "Action: Retry failed. Switching to next model.",
                        model,
                    )
                    metrics.fallback_reason = "Invalid JSON"
                    continue

            # --- Normalize ---
            normalised = self._normalize(parsed, metrics)

            # --- Validate ---
            if validator is not None:
                try:
                    if not validator(normalised):
                        raise LLMValidationError("Validator rejected the response")
                except LLMValidationError:
                    logger.warning(
                        "[%s] Model %s failed validation — switching models",
                        self._request_id,
                        model,
                    )
                    metrics.fallback_reason = "Validation failed"
                    continue
                except Exception as exc:
                    logger.warning(
                        "[%s] Model %s validator raised %s: %s",
                        self._request_id,
                        model,
                        type(exc).__name__,
                        exc,
                    )
                    metrics.fallback_reason = f"Validator error: {type(exc).__name__}"
                    continue

            # --- Success ---
            elapsed = time.monotonic() - start
            self._registry.record_success(model, elapsed)
            self._metrics_collector.record_success(model, elapsed)

            metrics.success = True
            metrics.final_model = model
            metrics.validation_passed = True
            metrics.total_time = elapsed

            self._log_success(metrics)
            self._log_summary(metrics)
            return (normalised, model, metrics.total_attempts)

        metrics.total_time = time.monotonic() - start
        metrics.fallback = True
        self._metrics_collector.record_fallback()
        self._log_summary(metrics)
        self._log_fallback(metrics, last_error)

        raise LLMAllModelsFailed(
            f"[{self._request_id}] All {len(models_to_try)} models exhausted "
            f"after {metrics.total_attempts} attempts. "
            f"Last error: {last_error}"
        ) from last_error

    _last_call_error: Exception | None = None

    @staticmethod
    def _categorize_error(error: Exception | None) -> str:
        if error is None:
            return "unknown"
        if isinstance(error, LLMRateLimitError):
            return "rate_limit"
        if isinstance(error, LLMTimeoutError):
            return "timeout"
        if isinstance(error, LLMHTTPError):
            if error.status_code == 404:
                return "model_not_found"
            if error.status_code in (500, 502, 503):
                return "server_error"
            if error.status_code == 0:
                return "connection_error"
            if error.status_code == 400:
                return "invalid_model"
            return f"http_{error.status_code}"
        return type(error).__name__

    @staticmethod
    def _is_immediate_switch(category: str) -> bool:
        return category in ("rate_limit", "model_not_found", "invalid_model")

    @staticmethod
    def _format_error_reason(error: Exception | None, category: str) -> str:
        if isinstance(error, LLMRateLimitError):
            return "HTTP 429"
        if isinstance(error, LLMTimeoutError):
            return "Timeout"
        if isinstance(error, LLMHTTPError):
            if category == "model_not_found":
                return "HTTP 404"
            if category == "server_error":
                return f"HTTP {error.status_code}"
            if category == "connection_error":
                return "Connection Error"
            if category == "invalid_model":
                return "HTTP 400 (invalid model)"
            return f"HTTP {error.status_code}"
        return category

    def _try_call(
        self,
        client: LLMClient,
        model: str,
        messages: Sequence[Mapping[str, Any]],
        temperature: float,
        max_tokens: int,
        metrics: LLMMetrics,
    ) -> tuple[str | None, bool]:
        self._last_call_error = None
        call_start = time.monotonic()
        try:
            raw = client.complete_chat(
                messages, temperature=temperature, max_tokens=max_tokens
            )
        except LLMTimeoutError as exc:
            self._last_call_error = exc
            self._registry.record_error(model)
            self._metrics_collector.record_timeout(model)
            logger.warning(
                "[%s] Model %s timed out after %.1fs — retryable",
                self._request_id,
                model,
                time.monotonic() - call_start,
            )
            return (None, True)
        except LLMRateLimitError as exc:
            self._last_call_error = exc
            self._registry.record_error(model)
            self._registry.mark_cooldown(model)
            self._metrics_collector.record_rate_limit(model)
            logger.warning(
                "[%s] Model %s rate limited (429) after %.1fs — retryable",
                self._request_id,
                model,
                time.monotonic() - call_start,
            )
            return (None, True)
        except LLMHTTPError as exc:
            self._last_call_error = exc
            elapsed = time.monotonic() - call_start
            self._registry.record_error(model)

            if self._registry.check_invalid_response(model, exc.status_code, str(exc)):
                logger.warning(
                    "[%s] Model %s invalid (HTTP %d) after %.1fs — removed",
                    self._request_id,
                    model,
                    exc.status_code,
                    elapsed,
                )
                return (None, False)

            if exc.is_retryable():
                logger.warning(
                    "[%s] Model %s HTTP %d after %.1fs — retryable",
                    self._request_id,
                    model,
                    exc.status_code,
                    elapsed,
                )
                return (None, True)

            logger.warning(
                "[%s] Model %s HTTP %d after %.1fs — not retryable",
                self._request_id,
                model,
                exc.status_code,
                elapsed,
            )
            return (None, False)
        except Exception as exc:
            self._last_call_error = exc
            self._registry.record_error(model)
            logger.warning(
                "[%s] Model %s unexpected error %s after %.1fs — not retryable",
                self._request_id,
                model,
                type(exc).__name__,
                time.monotonic() - call_start,
            )
            return (None, False)

        if not raw or not raw.strip():
            logger.warning(
                "[%s] Model %s empty response — not retryable",
                self._request_id,
                model,
            )
            return (None, False)

        metrics.response_size = len(raw)
        return (raw, False)

    def _resolve_client(self, model_idx: int, model: str) -> LLMClient:
        if model_idx == 0 and self._injected_client is not None:
            return self._injected_client
        return OpenAICompatibleLLMClient(
            base_url=self._base_url,
            model=model,
            api_key=self._api_key,
            timeout=self._timeout,
        )

    @staticmethod
    def _extract_first_json(text: str) -> str:
        start = text.find("{")
        if start == -1:
            return text

        depth = 0
        in_string = False
        escaped = False

        for i in range(start, len(text)):
            ch = text[i]

            if escaped:
                escaped = False
                continue

            if ch == "\\" and in_string:
                escaped = True
                continue

            if ch == '"':
                in_string = not in_string
                continue

            if in_string:
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]

        return text[start:]

    def _repair_and_parse(self, raw: str) -> dict[str, Any] | None:
        extracted = self._extract_first_json(raw.strip())
        if not extracted or (extracted == raw.strip() and "{" not in extracted):
            extracted = raw.strip()

        try:
            repaired = repair_json(extracted)
        except Exception:
            logger.debug(
                "[%s] json_repair failed | raw[:300]=%s",
                self._request_id,
                raw[:300],
            )
            return None

        try:
            parsed = json.loads(repaired)
        except json.JSONDecodeError:
            logger.debug(
                "[%s] json.loads after repair failed | repaired[:300]=%s",
                self._request_id,
                repaired[:300],
            )
            return None

        if not isinstance(parsed, dict):
            logger.debug(
                "[%s] Repaired JSON is not a dict (type=%s)",
                self._request_id,
                type(parsed).__name__,
            )
            return None

        return parsed

    def _normalize(self, parsed: dict[str, Any], metrics: LLMMetrics) -> dict[str, Any]:
        for key, default in _FIELD_DEFAULTS.items():
            if key not in parsed or parsed[key] is None:
                parsed[key] = default
                metrics.filled_fields.append(key)
            elif key in _RICH_FIELDS and isinstance(default, dict):
                for sub_key, sub_default in default.items():
                    if sub_key not in parsed[key] or parsed[key][sub_key] is None:
                        parsed[key][sub_key] = sub_default
                        metrics.filled_fields.append(f"{key}.{sub_key}")

        return parsed

    def _backoff(self, attempt: int) -> float:
        return self._backoff_base * (2**attempt)

    def _log_raw_parse_error(self, model: str, raw: str) -> None:
        logger.warning(
            "================ RAW LLM RESPONSE ================\n"
            "MODEL: %s\n"
            "\n"
            "%s\n"
            "==================================================",
            model,
            raw,
        )

    def _log_request_start(self, model: str, attempt: int) -> None:
        logger.info(
            "========================================================\n"
            "REQUEST ID: %s\n"
            "MODEL: %s\n"
            "ATTEMPT: %d\n"
            "TEMPERATURE: %.1f\n"
            "MAX TOKENS: %d\n"
            "========================================================",
            self._request_id,
            model,
            attempt + 1,
            settings.LLM_TEMPERATURE,
            settings.LLM_MAX_TOKENS,
        )

    def _maybe_log_raw_response(self, model: str, raw: str) -> None:
        if not settings.LLM_LOG_RAW_RESPONSES and not logger.isEnabledFor(
            logging.DEBUG
        ):
            return
        logger.info(
            "========================================================\n"
            "RAW LLM RESPONSE\n"
            "MODEL: %s\n"
            "\n"
            "%s\n"
            "========================================================",
            model,
            raw,
        )

    def _log_success(self, m: LLMMetrics) -> None:
        filled = ""
        if m.filled_fields:
            filled = f" | filled: {m.filled_fields}"
        logger.info(
            "[%s] SUCCESS — model: %s | attempts: %d | "
            "size: %d | parse: %.3fs | total: %.3fs%s",
            m.request_id,
            m.final_model,
            m.total_attempts,
            m.response_size,
            m.parse_time,
            m.total_time,
            filled,
        )

    def _log_summary(self, m: LLMMetrics) -> None:
        logger.info(
            "==================================================\n"
            "LLM SUMMARY\n"
            "==================================================\n"
            "analysis id:      %s\n"
            "selected model:   %s\n"
            "attempts:         %d\n"
            "fallback level:   %d\n"
            "fallback reason:  %s\n"
            "elapsed:          %.2fs\n"
            "fallback used:    %s\n"
            "response size:    %d\n"
            "validation:       %s\n"
            "==================================================",
            m.request_id,
            m.final_model or "N/A",
            m.total_attempts,
            m.fallback_level,
            m.fallback_reason or "N/A",
            m.total_time,
            "Yes" if m.fallback else "No",
            m.response_size,
            "Passed" if m.validation_passed else "Failed",
        )

    def _log_fallback(self, m: LLMMetrics, last_error: Exception | None) -> None:
        logger.warning(
            "[%s] FALLBACK — attempts: %d | total: %.3fs | "
            "fallback_level: %d | reason: %s | last_error: %s",
            m.request_id,
            m.total_attempts,
            m.total_time,
            m.fallback_level,
            m.fallback_reason or "N/A",
            last_error,
        )

    def health(self) -> dict[str, Any]:
        return self._registry.health()

    def stats(self) -> dict[str, Any]:
        base = self._metrics_collector.stats()
        base.update(self._cache.stats())
        return base
