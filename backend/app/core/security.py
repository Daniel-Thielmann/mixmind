from __future__ import annotations


def build_cors_origins(
    *,
    environment: str = "development",
    additional_origins: list[str] | None = None,
) -> list[str]:
    _origins: list[str] = additional_origins or []

    if environment == "development":
        _origins.extend(
            [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
            ]
        )
    elif environment == "production":
        _origins.extend(
            [
                "https://mixmind-ai.vercel.app",
            ]
        )

    return _origins
