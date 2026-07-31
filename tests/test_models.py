"""Tests for the ATLAS model provider system."""

import pytest

from atlas.config.settings import Settings
from atlas.models.base import ModelConfigurationError
from atlas.models.factory import create_model_provider
from atlas.models.mock import MockModelProvider
from atlas.models.ollama_provider import OllamaModelProvider
from atlas.models.openai_provider import OpenAIModelProvider


def test_factory_creates_mock_provider() -> None:
    """The factory should create the selected mock provider."""

    settings = Settings(
        provider="mock",
        model="mock-model",
        openai_api_key=None,
        ollama_host="http://localhost:11434",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, MockModelProvider)


def test_factory_creates_openai_provider() -> None:
    """The factory should create the selected OpenAI provider."""

    settings = Settings(
        provider="openai",
        model="gpt-5.5",
        openai_api_key="fake-api-key",
        ollama_host="http://localhost:11434",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, OpenAIModelProvider)


def test_factory_creates_ollama_provider() -> None:
    """The factory should create the selected Ollama provider."""

    settings = Settings(
        provider="ollama",
        model="qwen3:4b",
        openai_api_key=None,
        ollama_host="http://localhost:11434",
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, OllamaModelProvider)


def test_factory_rejects_unknown_provider() -> None:
    """The factory should reject unsupported providers."""

    settings = Settings(
        provider="unknown",
        model="test-model",
        openai_api_key=None,
        ollama_host="http://localhost:11434",
    )

    with pytest.raises(ModelConfigurationError):
        create_model_provider(settings)


def test_ollama_provider_rejects_empty_model() -> None:
    """The Ollama provider should require a model name."""

    with pytest.raises(ModelConfigurationError):
        OllamaModelProvider(
            model="",
            host="http://localhost:11434",
        )


def test_ollama_provider_rejects_empty_host() -> None:
    """The Ollama provider should require a host address."""

    with pytest.raises(ModelConfigurationError):
        OllamaModelProvider(
            model="qwen3:4b",
            host="",
        )
