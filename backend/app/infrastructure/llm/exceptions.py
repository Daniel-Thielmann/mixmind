"""Domain exceptions for the AI assistant layer."""

_RETRYABLE_STATUS_CODES = {0, 500, 502, 503, 504}


class LLMError(Exception):
    """Base exception for all LLM-related errors."""


class LLMTimeoutError(LLMError):
    """Raised when the LLM provider request times out."""


class LLMHTTPError(LLMError):
    """Raised when the LLM provider returns an HTTP error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}: {message}")

    def is_retryable(self) -> bool:
        """Return ``True`` for 429, 5xx — errors that may succeed on retry (M2)."""
        return self.status_code in _RETRYABLE_STATUS_CODES


class LLMRateLimitError(LLMHTTPError):
    """Raised on HTTP 429 — rate limited."""


class LLMParsingError(LLMError):
    """Raised when the LLM response cannot be parsed as JSON."""


class LLMValidationError(LLMError):
    """Raised when the LLM response fails Pydantic validation."""


class LLMAllModelsFailed(LLMError):
    """Raised when every model in the fallback chain has been exhausted."""
