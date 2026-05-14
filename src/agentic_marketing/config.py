"""Pydantic settings loaded from environment and .env file."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


class DatabaseSettings(BaseSettings):
    """PostgreSQL connection settings."""

    model_config = SettingsConfigDict(env_prefix="DB_", extra="ignore")

    host: str = "localhost"
    port: int = 5432
    name: str = "agentic_marketing"
    user: str = "postgres"
    password: SecretStr = SecretStr("postgres")
    pool_size: int = 10
    max_overflow: int = 20

    @property
    def url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"


class MongoSettings(BaseSettings):
    """MongoDB connection settings."""

    model_config = SettingsConfigDict(env_prefix="MONGO_", extra="ignore")

    host: str = "localhost"
    port: int = 27017
    name: str = "agentic_marketing"
    user: str = ""
    password: SecretStr = SecretStr("")

    @property
    def url(self) -> str:
        if self.user and self.password.get_secret_value():
            return f"mongodb://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.name}"
        return f"mongodb://{self.host}:{self.port}/{self.name}"


class QdrantSettings(BaseSettings):
    """Qdrant vector store settings."""

    model_config = SettingsConfigDict(env_prefix="QDRANT_", extra="ignore")

    host: str = "localhost"
    port: int = 6333
    collection_name: str = "marketing_content"
    vector_size: int = 1536  # OpenAI text-embedding-3-small
    distance: str = "Cosine"


class LLMProviderSettings(BaseSettings):
    """LLM provider API keys and endpoints."""

    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

    openai_api_key: SecretStr | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    anthropic_api_key: SecretStr | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    default_model: str = "gpt-4o"
    default_temperature: float = 0.7


class PipelineSettings(BaseSettings):
    """Pipeline execution settings."""

    model_config = SettingsConfigDict(env_prefix="PIPELINE_", extra="ignore")

    manifest_path: Path = Path(__file__).resolve().parents[3] / "pipeline_defs" / "agentic-marketing.yaml"
    skills_base_path: Path = Path(__file__).resolve().parents[3] / "skills"
    checkpoint_policy: str = "guided"
    max_revisions_per_stage: int = 3
    max_send_backs: int = 2
    max_wall_time_minutes: int = 30
    budget_default_usd: float = 5.00


class AppSettings(BaseSettings):
    """Application-wide settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Agentic Marketing"
    debug: bool = False
    log_level: str = "INFO"
    decision_log_path: Path = Path.home() / ".agentic-marketing" / "decision_logs"
    artifacts_path: Path = Path.home() / ".agentic-marketing" / "artifacts"

    # Budget policies
    budget_enforcement: str = "warn"  # warn | cap | observe
    budget_reserve_holdback_pct: float = 0.10
    budget_single_action_approval_threshold: float = 0.50

    # Channel defaults
    channel_allocation_organic: float = 0.15
    channel_allocation_paid: float = 0.80
    channel_allocation_email: float = 0.05

    # Feature flags
    enable_human_approval_gates: bool = True
    enable_decision_logging: bool = True


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached merged settings (all sources combined)."""
    return AppSettings()


@dataclass
class MergedSettings:
    """Convenience access to all settings namespaces."""

    database: DatabaseSettings
    mongo: MongoSettings
    qdrant: QdrantSettings
    llm: LLMProviderSettings
    pipeline: PipelineSettings
    app: AppSettings

    @classmethod
    def from_env(cls) -> MergedSettings:
        return cls(
            database=DatabaseSettings(),
            mongo=MongoSettings(),
            qdrant=QdrantSettings(),
            llm=LLMProviderSettings(),
            pipeline=PipelineSettings(),
            app=AppSettings(),
        )

    def ensure_paths(self) -> None:
        """Create on-disk paths that must exist."""
        for p in [self.app.decision_log_path, self.app.artifacts_path]:
            p.mkdir(parents=True, exist_ok=True)


from dataclasses import dataclass