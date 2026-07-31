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
    log_directory: Path
    log_level: str
    log_max_bytes: int
    log_backup_count: int


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

    log_directory_value = os.getenv(
        "ATLAS_LOG_DIRECTORY",
        "logs",
    ).strip()

    log_level = (
        os.getenv(
            "ATLAS_LOG_LEVEL",
            "INFO",
        )
        .strip()
        .upper()
    )

    log_max_bytes = _load_integer(
        variable_name="ATLAS_LOG_MAX_BYTES",
        default=5_000_000,
        minimum=1,
    )

    log_backup_count = _load_integer(
        variable_name="ATLAS_LOG_BACKUP_COUNT",
        default=5,
        minimum=0,
    )

    if not model:
        raise ModelConfigurationError("ATLAS_MODEL cannot be empty.")

    if not ollama_host:
        raise ModelConfigurationError("OLLAMA_HOST cannot be empty.")

    if not memory_database_value:
        raise ModelConfigurationError("ATLAS_MEMORY_DATABASE cannot be empty.")

    if not log_directory_value:
        raise ModelConfigurationError("ATLAS_LOG_DIRECTORY cannot be empty.")

    return Settings(
        provider=provider,
        model=model,
        openai_api_key=openai_api_key,
        ollama_host=ollama_host,
        memory_database_path=Path(memory_database_value),
        log_directory=Path(log_directory_value),
        log_level=log_level,
        log_max_bytes=log_max_bytes,
        log_backup_count=log_backup_count,
    )


def _load_integer(
    variable_name: str,
    default: int,
    minimum: int,
) -> int:
    """Load and validate an integer environment variable."""
    raw_value = os.getenv(
        variable_name,
        str(default),
    ).strip()

    try:
        value = int(raw_value)
    except ValueError as error:
        raise ModelConfigurationError(f"{variable_name} must be an integer.") from error

    if value < minimum:
        raise ModelConfigurationError(f"{variable_name} must be at least {minimum}.")

    return value
