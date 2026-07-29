"""Tests for the ATLAS core application."""

from atlas.core.app import AtlasApp
from atlas.models.mock import MockModelProvider


def test_app_uses_model_provider() -> None:
    """ATLAS Core should send messages to its model provider."""
    app = AtlasApp(model_provider=MockModelProvider())

    response = app.process_message("Test message")

    assert response == "Mock response to: Test message"


def test_app_handles_empty_messages() -> None:
    """ATLAS Core should safely handle empty input."""
    app = AtlasApp(model_provider=MockModelProvider())

    response = app.process_message("   ")

    assert response == "I did not receive a message."


def test_app_reports_provider_name() -> None:
    """ATLAS Core should expose the active provider name."""
    app = AtlasApp(model_provider=MockModelProvider())

    assert app.provider_name == "Mock"
