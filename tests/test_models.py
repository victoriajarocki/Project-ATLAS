"""Tests for ATLAS model providers and provider creation."""

import pytest

from atlas.config.settings import Settings
from atlas.models.base import ModelConfigurationError
from atlas.models.factory import create_model_provider
from atlas.models.mock import MockModelProvider


def test_mock_provider_response() -> None:
    """The mock provider should return a deterministic response."""
    provider = MockModelProvider()

    response = provider.generate_response("Hello")

    assert response == "Mock response to: Hello"


def test_factory_creates_mock_provider() -> None:
    """The factory should create the selected mock provider."""
    settings = Settings(
        provider="mock",
        model="test-model",
        openai_api_key=None,
    )

    provider = create_model_provider(settings)

    assert isinstance(provider, MockModelProvider)


def test_factory_rejects_unknown_provider() -> None:
    """The factory should reject unsupported provider names."""
    settings = Settings(
        provider="unknown",
        model="test-model",
        openai_api_key=None,
    )

    with pytest.raises(ModelConfigurationError):
        create_model_provider(settings)
