from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1500,
        timeout: int = 30,
    ) -> tuple[str, str]: ...

    @abstractmethod
    async def health(self) -> dict[str, Any]: ...


class CacheProvider(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, ttl: int) -> None: ...

    def clear(self) -> None: ...
