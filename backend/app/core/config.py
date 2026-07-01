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
