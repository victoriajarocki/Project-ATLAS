"""Environment-based configuration for Project ATLAS."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from atlas.models.base import ModelConfigurationError


@dataclass(frozen=True)
class Settings:
    """Configuration values used by the ATLAS application."""

    provider: str
    model: str
    openai_api_key: str | None
    ollama_host: str
    memory_database_path: Path


def load_settings() -> Settings:
    """Load ATLAS settings from environment variables."""
    load_dotenv()

    provider = (
        os.getenv(
            "ATLAS_PROVIDER",
            "mock",
        )
        .strip()
        .lower()
    )

    model = os.getenv(
        "ATLAS_MODEL",
        "mock-model",
    ).strip()

    openai_api_key = os.getenv("OPENAI_API_KEY")

    ollama_host = os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434",
    ).strip()

    memory_database_value = os.getenv(
        "ATLAS_MEMORY_DATABASE",
        "data/atlas_memory.db",
    ).strip()

    if not model:
        raise ModelConfigurationError("ATLAS_MODEL cannot be empty.")

    if not ollama_host:
        raise ModelConfigurationError("OLLAMA_HOST cannot be empty.")

    if not memory_database_value:
        raise ModelConfigurationError("ATLAS_MEMORY_DATABASE cannot be empty.")

    return Settings(
        provider=provider,
        model=model,
        openai_api_key=openai_api_key,
        ollama_host=ollama_host,
        memory_database_path=Path(memory_database_value),
    )
