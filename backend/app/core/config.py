from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Centraliza todas as configurações da aplicação.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    APP_NAME: str = "MixMind AI"
    APP_VERSION: str = "0.1.0"

    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    TEMP_DIR: str = "temp"

    MAX_UPLOAD_SIZE: int = Field(
        default=100,
        description="Maximum upload size in MB",
    )

    BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Base URL for constructing public file URLs.",
    )

    # ------------------------------------------------------------------
    # LLM / AI configuration (M12)
    # ------------------------------------------------------------------

    OPENROUTER_API_KEY: str = Field(
        default="",
        description="API key for OpenAI-compatible LLM providers.",
    )
    OPENROUTER_MODEL: str = Field(
        default="openai/gpt-oss-120b:free",
        description="Primary model identifier used by the DJ assistant.",
    )
    OPENROUTER_MODELS: list[str] = Field(
        default_factory=lambda: [
            "google/gemma-4-31b-it:free",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "poolside/laguna-m1:free",
        ],
        description="Fallback model chain (tried in order after primary model).",
    )
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenAI-compatible base URL for the LLM provider.",
    )

    LLM_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Per-model request timeout in seconds (M1).",
    )
    LLM_MAX_RETRIES: int = Field(
        default=2,
        ge=0,
        le=5,
        description="Max retry attempts per model (M2).",
    )
    LLM_RETRY_BACKOFF_BASE: float = Field(
        default=1.0,
        ge=0.5,
        le=10.0,
        description="Base backoff delay in seconds (doubles each retry, M2).",
    )
    LLM_MAX_TOKENS: int = Field(
        default=1500,
        ge=256,
        le=4096,
        description="Max tokens in LLM response.",
    )
    LLM_TEMPERATURE: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature.",
    )
    LLM_LOG_RAW_RESPONSES: bool = Field(
        default=False,
        description="Log full raw LLM responses (M5).",
    )

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


settings = Settings()
