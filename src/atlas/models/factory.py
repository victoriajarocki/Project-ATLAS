"""Factory for creating configured ATLAS model providers."""

from atlas.config.settings import Settings
from atlas.models.base import ModelConfigurationError, ModelProvider
from atlas.models.mock import MockModelProvider
from atlas.models.openai_provider import OpenAIModelProvider


def create_model_provider(settings: Settings) -> ModelProvider:
    """Create the model provider selected in the ATLAS settings."""
    if settings.provider == "mock":
        return MockModelProvider()

    if settings.provider == "openai":
        return OpenAIModelProvider(
            api_key=settings.openai_api_key,
            model=settings.model,
        )

    raise ModelConfigurationError(
        f"Unsupported ATLAS provider: {settings.provider!r}. "
        "Supported providers are 'mock' and 'openai'."
    )
