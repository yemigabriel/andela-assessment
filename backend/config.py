import json
import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4.1-mini"
    mcp_server_url: str = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
    agent_name: str = "Meridian Electronics Support Agent"
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ALLOW_ORIGINS")
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    memory_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("MEMORY_DIR", "memory")),
        alias="MEMORY_DIR",
    )
    memory_s3_bucket: str | None = Field(default=None, alias="MEMORY_S3_BUCKET")
    aws_region: str | None = Field(default=None, alias="AWS_REGION")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_cors_origins(self) -> list[str]:
        stripped = self.cors_origins.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            return [str(item) for item in json.loads(stripped)]
        return [item.strip() for item in stripped.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
