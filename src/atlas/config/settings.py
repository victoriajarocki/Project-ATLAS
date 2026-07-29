"""Environment-based configuration for Project ATLAS."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from atlas.models.base import ModelConfigurationError


@dataclass(frozen=True)
class Settings:
    """Configuration values used by the ATLAS application."""

    provider: str
    model: str
    openai_api_key: str | None


def load_settings() -> Settings:
    """Load ATLAS settings from environment variables."""
    load_dotenv()

    provider = os.getenv("ATLAS_PROVIDER", "mock").strip().lower()
    model = os.getenv("ATLAS_MODEL", "gpt-5.5").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not model:
        raise ModelConfigurationError("ATLAS_MODEL cannot be empty.")

    return Settings(
        provider=provider,
        model=model,
        openai_api_key=openai_api_key,
    )
