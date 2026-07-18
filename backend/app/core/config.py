from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = "MixMind AI"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "AI-powered assistant for DJs capable of analyzing electronic music tracks "
        "using Digital Signal Processing (DSP) and Music Information Retrieval (MIR)."
    )
    ENVIRONMENT: str = Field(
        default="development", pattern=r"^(development|staging|production)$"
    )
    DEBUG: bool = Field(default=False)
    LOG_LEVEL: str = Field(
        default="INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    LOG_JSON_FORMAT: bool = Field(default=False)

    API_V1_PREFIX: str = "/api/v1"

    CORS_ORIGINS: list[str] = Field(default_factory=list)
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default_factory=lambda: ["*"])

    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    TEMP_DIR: str = "temp"

    MAX_UPLOAD_SIZE: int = Field(default=100, ge=1, le=500)

    BASE_URL: str = Field(default="http://localhost:8000")

    SUPABASE_URL: str = Field(default="")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", repr=False)
    SUPABASE_DEMO_BUCKET: str = Field(default="mixmind-media")
    DEMO_SIGNED_URL_TTL: int = Field(default=3600, ge=300, le=86400)
    DEMO_MANIFEST_CACHE_TTL: int = Field(default=300, ge=0, le=3500)

    OPENROUTER_API_KEY: str = Field(default="")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1")
    OPENROUTER_MODEL: str = Field(default="openai/gpt-oss-20b:free")

    OPENROUTER_MODELS: list[str] = Field(
        default_factory=lambda: [
            "qwen/qwen3-next-80b-a3b-instruct",
            "google/gemma-4-31b-it:free",
            "google/gemma-4-26b-a4b-it:free",
            "tencent/hy3:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "poolside/laguna-m.1:free",
            "qwen/qwen3-next-80b-a3b-instruct:free",
            "qwen/qwen3-coder:free",
            "nvidia/nemotron-3.5-content-safety:free",
            "meta-llama/llama-3.3-70b-instruct:free",
            "meta-llama/llama-3.2-3b-instruct:free",
            "nvidia/nemotron-3-super-120b-a12b:free",
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "mistralai/mistral-medium-3.5-128b",
            "mistralai/mistral-small-4-119b-2603",
            "nvidia/nemotron-mini-4b-instruct",
        ]
    )

    LLM_TIMEOUT: int = Field(default=30, ge=5, le=120)
    LLM_MAX_RETRIES: int = Field(default=2, ge=0, le=5)
    LLM_RETRY_BACKOFF_BASE: float = Field(default=1.0, ge=0.5, le=10.0)
    LLM_MAX_TOKENS: int = Field(default=1500, ge=256, le=4096)
    LLM_TEMPERATURE: float = Field(default=0.0, ge=0.0, le=2.0)
    LLM_LOG_RAW_RESPONSES: bool = Field(default=False)

    @property
    def upload_path(self) -> Path:
        return BASE_DIR / self.UPLOAD_DIR

    @property
    def processed_path(self) -> Path:
        return BASE_DIR / self.PROCESSED_DIR

    @property
    def temp_path(self) -> Path:
        return BASE_DIR / self.TEMP_DIR

    @property
    def analysis_path(self) -> Path:
        return self.processed_path / "analysis"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"


settings = Settings()
