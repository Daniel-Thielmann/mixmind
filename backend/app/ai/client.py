"""OpenAI-compatible LLM client abstractions."""

from __future__ import annotations

import logging
from typing import Any, Mapping, Protocol, Sequence

import httpx
from app.ai.exceptions import (
    LLMHTTPError,
    LLMRateLimitError,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class LLMClient(Protocol):
    """Abstract contract for chat-completion style LLM providers."""

    def complete_chat(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Return the assistant content for a chat completion request.

        Raises:
            LLMTimeoutError: On connection or read timeout.
            LLMRateLimitError: On HTTP 429.
            LLMHTTPError: On other HTTP errors.
            ValueError: If the response is structurally invalid.
        """
        ...


class OpenAICompatibleLLMClient:
    """HTTP client for OpenAI-compatible providers."""

    def __init__(
        self,
        base_url: str,
        model: str,
        api_key: str = "",
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self.model = model
        self._api_key = api_key
        self._client = client or httpx.Client(timeout=timeout)

    def complete_chat(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        temperature: float,
        max_tokens: int,
    ) -> str:
        url = f"{self._base_url}/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "MixMind AI",
        }

        logger.debug("POST %s | model: %s", url, self.model)

        try:
            response = self._client.post(url, json=payload, headers=headers)
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                f"Request timed out for model {self.model}: {exc}"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMHTTPError(0, f"HTTP error for model {self.model}: {exc}") from exc

        if response.status_code == 429:
            raise LLMRateLimitError(
                429,
                f"Rate limited on model {self.model}: {response.text[:300]}",
            )
        if response.status_code >= 400:
            raise LLMHTTPError(
                response.status_code,
                f"Model {self.model} returned HTTP {response.status_code}: "
                f"{response.text[:500]}",
            )

        data = response.json()

        choices = data.get("choices")
        if not choices:
            raise ValueError(f"No choices returned for model {self.model}.\n{data}")

        message = choices[0].get("message", {})
        content = message.get("content")

        if not isinstance(content, str):
            raise ValueError(
                f"Invalid assistant content for model {self.model}.\n{data}"
            )

        return content
