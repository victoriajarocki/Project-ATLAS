"""Tests for the initial ATLAS command-line interface."""

from atlas.main import create_response


def test_greeting_response() -> None:
    """ATLAS should identify itself when greeted."""
    response = create_response("hello")

    assert response == "Hello, Victoria. ATLAS is online."


def test_empty_message_response() -> None:
    """ATLAS should handle empty input safely."""
    response = create_response("   ")

    assert response == "I did not receive a message."


def test_unknown_message_is_acknowledged() -> None:
    """ATLAS should acknowledge messages it cannot yet process."""
    response = create_response("Explain orbital mechanics")

    assert response == "I received your message: Explain orbital mechanics"
