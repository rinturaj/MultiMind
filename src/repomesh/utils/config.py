"""
Configuration management for RepoMesh AI.

This module provides centralized configuration using Pydantic settings
with environment variable support.
"""

from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="RepoMesh AI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    app_env: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes")
    api_workers: int = Field(default=1, description="Number of worker processes")

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model")
    openai_temperature: float = Field(default=0.7, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=4096, description="OpenAI max tokens")

    # Repository Configuration
    repos_base_path: str = Field(default="./repos", description="Base path for repositories")
    max_repo_size_mb: int = Field(default=500, description="Maximum repository size in MB")
    clone_timeout_seconds: int = Field(default=300, description="Repository clone timeout")

    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        description="ChromaDB persistence directory",
    )
    chroma_collection_name: str = Field(
        default="repomesh_context",
        description="ChromaDB collection name",
    )
    chroma_embedding_model: str = Field(
        default="text-embedding-ada-002",
        description="Embedding model for ChromaDB",
    )

    # Agent Configuration
    max_concurrent_agents: int = Field(default=5, description="Maximum concurrent agents")
    agent_timeout_seconds: int = Field(default=300, description="Agent execution timeout")
    agent_retry_attempts: int = Field(default=3, description="Agent retry attempts")

    # Orchestration Configuration
    max_orchestration_steps: int = Field(
        default=50,
        description="Maximum orchestration steps",
    )
    orchestration_timeout_seconds: int = Field(
        default=600,
        description="Orchestration timeout",
    )

    # Event System Configuration
    event_history_max_size: int = Field(
        default=1000,
        description="Maximum event history size",
    )
    event_retention_hours: int = Field(default=24, description="Event retention period")

    # Context Configuration
    context_search_top_k: int = Field(default=10, description="Context search top K results")
    context_similarity_threshold: float = Field(
        default=0.7,
        description="Context similarity threshold",
    )

    # Security Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )
    cors_allow_credentials: bool = Field(default=True, description="CORS allow credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="CORS allowed methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="CORS allowed headers")

    # Monitoring Configuration
    enable_tracing: bool = Field(default=True, description="Enable execution tracing")
    trace_output_dir: str = Field(default="./traces", description="Trace output directory")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")

    def get_repos_path(self) -> Path:
        """Get repositories base path as Path object."""
        return Path(self.repos_base_path)

    def get_chroma_path(self) -> Path:
        """Get ChromaDB persistence path as Path object."""
        return Path(self.chroma_persist_directory)

    def get_trace_path(self) -> Path:
        """Get trace output path as Path object."""
        return Path(self.trace_output_dir)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get global settings instance.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Returns:
        New settings instance
    """
    global _settings
    _settings = Settings()
    return _settings

# Made with Bob
