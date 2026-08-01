"""Tests for the ATLAS model provider system."""

from pathlib import Path

import pytest

from atlas.config.settings import Settings
from atlas.models.base import ModelConfigurationError
from atlas.models.factory import create_model_provider
from atlas.models.mock import MockModelProvider
from atlas.models.ollama_provider import OllamaModelProvider
from atlas.models.openai_provider import OpenAIModelProvider


def create_test_settings(
    provider: str,
    model: str = "test-model",
    openai_api_key: str | None = None,
) -> Settings:
    """Create settings used by model provider tests."""
    return Settings(
        provider=provider,
        model=model,
        openai_api_key=openai_api_key,
        ollama_host="http://localhost:11434",
        memory_database_path=Path("data/test_memory.db"),
        log_directory=Path("logs"),
        log_level="INFO",
        log_max_bytes=5_000_000,
        log_backup_count=5,
        allowed_directories=(Path("workspace"),),
        filesystem_max_read_bytes=1_000_000,
        filesystem_max_write_characters=1_000_000,
    )


def test_mock_provider_response() -> None:
    """The mock provider should return a deterministic response."""
    provider = MockModelProvider()

    response = provider.generate_response("Hello")

    assert response == "Mock response to: Hello"


def test_factory_creates_mock_provider() -> None:
    """The factory should create the selected mock provider."""
    settings = create_test_settings(provider="mock")

    provider = create_model_provider(settings)

    assert isinstance(provider, MockModelProvider)


def test_factory_creates_openai_provider() -> None:
    """The factory should create the selected OpenAI provider."""
    settings = create_test_settings(
        provider="openai",
        model="test-openai-model",
        openai_api_key="test-api-key",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, OpenAIModelProvider)


def test_factory_creates_ollama_provider() -> None:
    """The factory should create the selected Ollama provider."""
    settings = create_test_settings(
        provider="ollama",
        model="qwen3:4b",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, OllamaModelProvider)


def test_factory_rejects_unknown_provider() -> None:
    """The factory should reject unsupported provider names."""
    settings = create_test_settings(provider="unknown")

    with pytest.raises(ModelConfigurationError):
        create_model_provider(settings)


def test_ollama_provider_rejects_empty_model() -> None:
    """The Ollama provider should require a model name."""
    with pytest.raises(ModelConfigurationError):
        OllamaModelProvider(
            model="   ",
            host="http://localhost:11434",
        )


def test_ollama_provider_rejects_empty_host() -> None:
    """The Ollama provider should require a host address."""
    with pytest.raises(ModelConfigurationError):
        OllamaModelProvider(
            model="qwen3:4b",
            host="   ",
        )
