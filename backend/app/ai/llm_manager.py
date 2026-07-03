"""Orchestrates model fallback, retry, JSON repair, and schema validation."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from app.ai.client import LLMClient, OpenAICompatibleLLMClient
from app.ai.exceptions import (
    LLMAllModelsFailed,
    LLMHTTPError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMValidationError,
)
from app.core.config import settings
from json_repair import repair_json

logger = logging.getLogger(__name__)

# Default values injected when a field is missing from the LLM response.
_FIELD_DEFAULTS: dict[str, Any] = {
    "summary": "No summary provided.",
    "mix_direction": "No direction provided.",
    "transition_quality": "Medium",
    "transition_type": "Standard blend",
    "confidence": 50,
    "tempo_analysis": {
        "difference": "No tempo analysis available.",
        "recommendation": "Match tempos manually.",
    },
    "energy_analysis": {
        "difference": "No energy analysis available.",
        "recommendation": "Use your ears to match energy.",
    },
    "compatibility_analysis": {
        "score": "No score available.",
        "interpretation": "Interpretation unavailable.",
    },
    "mix_strategy": {
        "before_transition": "Prepare your cue points.",
        "during_transition": "Use a standard blend.",
        "after_transition": "Monitor the mix.",
    },
    "dj_execution": {
        "loop": "Set a loop as needed.",
        "eq": "Use standard EQ technique.",
        "filter": "Apply filter as desired.",
        "tempo_fader": "No recommendation.",
        "phrase_matching": "No recommendation.",
        "cue_point": "No recommendation.",
    },
    "club_tip": "",
    "professional_notes": "",
    "risks": [],
    "best_use_case": "",
    "risk_level": "Medium",
    "alternative_strategy": "",
    "why_this_strategy": "",
    "transition_timeline": {},
}

_RICH_FIELDS = {
    "tempo_analysis",
    "energy_analysis",
    "compatibility_analysis",
    "mix_strategy",
    "dj_execution",
}


@dataclass
class LLMMetrics:
    """Collects observability data for one LLM request cycle."""

    request_id: str = ""
    model_attempts: list[str] = field(default_factory=list)
    total_attempts: int = 0
    repair_count: int = 0
    parse_time: float = 0.0
    total_time: float = 0.0
    success: bool = False
    final_model: str = ""
    fallback: bool = False
    filled_fields: list[str] = field(default_factory=list)
    response_size: int = 0
    finish_reason: str = ""
    validation_passed: bool = False


class LLMManager:
    """Orchestrates the full LLM lifecycle: model fallback, retry, repair, parsing.

    Configuration (from ``app.core.config.settings``):

    * ``LLM_TIMEOUT`` — per-model timeout
    * ``LLM_MAX_RETRIES`` — retry attempts per model
    * ``LLM_RETRY_BACKOFF_BASE`` — exponential backoff base (seconds)

    Retry happens only on retryable errors (HTTP 429, 5xx, timeout).
    Invalid JSON, validation errors, and empty responses are never retried.

    Raw responses are logged only when ``LLM_LOG_RAW_RESPONSES`` is ``True``
    or the logger level is ``DEBUG``.
    """

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
    ) -> None:
        self._models = models
        self._base_url = base_url
        self._api_key = api_key
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        validator: Callable[[dict[str, Any]], bool] | None = None,
    ) -> tuple[dict[str, Any], str, int]:
        """Try each model in the chain: call → repair → normalise → validate.

        Args:
            messages: OpenAI-style chat messages (system + user).
            temperature: Sampling temperature.
            max_tokens: Max tokens in the response.
            validator: Optional callback that receives the normalised dict
                and returns ``True`` if it is acceptable.  When the callback
                returns ``False`` the attempt is treated as a failure.

        Returns:
            ``(parsed_dict, model_name, total_attempts)``.

        Raises:
            LLMAllModelsFailed: When every model has been exhausted.
        """
        metrics = LLMMetrics(request_id=self._request_id)
        start = time.monotonic()

        last_error: Exception | None = None

        for model_idx, model in enumerate(self._models):
            if model_idx > 0 and self._injected_client is not None:
                logger.info(
                    "[%s] Skipping fallback model %s (injected client in use)",
                    self._request_id,
                    model,
                )
                break

            client = self._resolve_client(model_idx, model)

            for attempt in range(self._max_retries):
                metrics.total_attempts += 1
                metrics.model_attempts.append(f"{model}#{attempt + 1}")

                self._log_request_start(model, attempt)

                # --- Call ---
                raw, retryable = self._try_call(
                    client, messages, temperature, max_tokens, metrics
                )
                if raw is None:
                    last_error = self._last_call_error
                    if retryable and attempt < self._max_retries - 1:
                        delay = self._backoff(attempt)
                        logger.info(
                            "[%s] Retrying model %s in %.1fs (attempt %d/%d)",
                            self._request_id,
                            model,
                            delay,
                            attempt + 1,
                            self._max_retries,
                        )
                        time.sleep(delay)
                    continue

                # --- Raw response logging (M5) ---
                self._maybe_log_raw_response(model, raw)

                # --- Parse ---
                parsed = self._repair_and_parse(raw)
                if parsed is None:
                    logger.warning(
                        "[%s] Model %s returned unparseable JSON — skipping retry",
                        self._request_id,
                        model,
                    )
                    # Invalid JSON is NOT retryable — move to next model.
                    break

                # --- Normalise ---
                normalised = self._normalize(parsed, metrics)

                # --- Validate ---
                if validator is not None:
                    try:
                        if not validator(normalised):
                            raise LLMValidationError("Validator rejected the response")
                    except LLMValidationError:
                        logger.warning(
                            "[%s] Model %s failed validation — skipping retry",
                            self._request_id,
                            model,
                        )
                        # Validation failure is NOT retryable.
                        break
                    except Exception as exc:
                        logger.warning(
                            "[%s] Model %s validator raised %s: %s",
                            self._request_id,
                            model,
                            type(exc).__name__,
                            exc,
                        )
                        if attempt < self._max_retries - 1:
                            time.sleep(self._backoff(attempt))
                        continue

                # --- Success ---
                metrics.success = True
                metrics.final_model = model
                metrics.validation_passed = True
                metrics.total_time = time.monotonic() - start

                self._log_success(metrics)
                self._log_summary(metrics)
                return (normalised, model, metrics.total_attempts)

        # --- All models exhausted ---
        metrics.total_time = time.monotonic() - start
        metrics.fallback = True
        self._log_summary(metrics)
        self._log_fallback(metrics, last_error)

        raise LLMAllModelsFailed(
            f"[{self._request_id}] All {len(self._models)} models exhausted "
            f"after {metrics.total_attempts} attempts. "
            f"Last error: {last_error}"
        ) from last_error

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    _last_call_error: Exception | None = None

    def _try_call(
        self,
        client: LLMClient,
        messages: Sequence[Mapping[str, Any]],
        temperature: float,
        max_tokens: int,
        metrics: LLMMetrics,
    ) -> tuple[str | None, bool]:
        """Call the model and return ``(response, is_retryable)``.

        Returns ``(None, True)`` for retryable errors (timeout, 429, 5xx).
        Returns ``(None, False)`` for non-retryable errors.
        """
        self._last_call_error = None
        try:
            raw = client.complete_chat(
                messages, temperature=temperature, max_tokens=max_tokens
            )
        except LLMTimeoutError as exc:
            self._last_call_error = exc
            logger.warning(
                "[%s] Model timed out — retryable",
                self._request_id,
            )
            return (None, True)
        except LLMRateLimitError as exc:
            self._last_call_error = exc
            logger.warning(
                "[%s] Rate limited (429) — retryable",
                self._request_id,
            )
            return (None, True)
        except LLMHTTPError as exc:
            self._last_call_error = exc
            if exc.is_retryable():
                logger.warning(
                    "[%s] HTTP %d — retryable",
                    self._request_id,
                    exc.status_code,
                )
                return (None, True)
            logger.warning(
                "[%s] HTTP %d — not retryable, moving to next model",
                self._request_id,
                exc.status_code,
            )
            return (None, False)
        except Exception as exc:
            self._last_call_error = exc
            logger.warning(
                "[%s] Unexpected error %s — not retryable",
                self._request_id,
                type(exc).__name__,
            )
            return (None, False)

        if not raw or not raw.strip():
            logger.warning(
                "[%s] Empty response — not retryable",
                self._request_id,
            )
            return (None, False)

        metrics.response_size = len(raw)
        return (raw, False)

    def _resolve_client(self, model_idx: int, model: str) -> LLMClient:
        """Return a client for the given model index."""
        if model_idx == 0 and self._injected_client is not None:
            return self._injected_client
        return OpenAICompatibleLLMClient(
            base_url=self._base_url,
            model=model,
            api_key=self._api_key,
            timeout=self._timeout,
        )

    # ------------------------------------------------------------------
    # JSON extraction, repair & parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_first_json(text: str) -> str:
        """Find the first complete JSON object, respecting string contents."""
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
        """Extract the first JSON object, repair, then parse.

        Returns the parsed dict, or ``None`` if repair/parse fails.
        """
        extracted = self._extract_first_json(raw.strip())
        if not extracted or extracted == raw.strip() and "{" not in extracted:
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

    # ------------------------------------------------------------------
    # Normalisation — fill missing fields
    # ------------------------------------------------------------------

    def _normalize(self, parsed: dict[str, Any], metrics: LLMMetrics) -> dict[str, Any]:
        """Fill missing top-level and nested fields with defaults."""
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

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _backoff(self, attempt: int) -> float:
        """Exponential backoff: base, base*2, base*4 (M2)."""
        return self._backoff_base * (2**attempt)

    # ------------------------------------------------------------------
    # Structured logging (M4)
    # ------------------------------------------------------------------

    def _log_request_start(self, model: str, attempt: int) -> None:
        """Log before calling the model."""
        logger.info(
            "========================================================\n"
            "REQUEST ID: %s\n"
            "MODEL: %s\n"
            "ATTEMPT: %d/%d\n"
            "TEMPERATURE: %.1f\n"
            "MAX TOKENS: %d\n"
            "========================================================",
            self._request_id,
            model,
            attempt + 1,
            self._max_retries,
            settings.LLM_TEMPERATURE,
            settings.LLM_MAX_TOKENS,
        )

    def _maybe_log_raw_response(self, model: str, raw: str) -> None:
        """Log raw response only when DEBUG or ``LLM_LOG_RAW_RESPONSES`` (M5)."""
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
        """Log successful completion."""
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
        """Print the LLM SUMMARY block (M4)."""
        logger.info(
            "==================================================\n"
            "LLM SUMMARY\n"
            "==================================================\n"
            "analysis id:   %s\n"
            "selected model: %s\n"
            "elapsed:       %.2fs\n"
            "fallback used: %s\n"
            "retry count:   %d\n"
            "response size: %d\n"
            "validation:    %s\n"
            "==================================================",
            m.request_id,
            m.final_model or "N/A",
            m.total_time,
            "Yes" if m.fallback else "No",
            m.total_attempts - 1,
            m.response_size,
            "Passed" if m.validation_passed else "Failed",
        )

    def _log_fallback(self, m: LLMMetrics, last_error: Exception | None) -> None:
        """Log fallback after all models fail."""
        logger.warning(
            "[%s] FALLBACK — attempts: %d | total: %.3fs | last_error: %s",
            m.request_id,
            m.total_attempts,
            m.total_time,
            last_error,
        )
