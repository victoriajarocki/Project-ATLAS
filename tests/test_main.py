"""Basic tests for the ATLAS command-line module."""

from atlas.main import ATLAS_NAME, ATLAS_VERSION, EXIT_COMMANDS


def test_application_identity() -> None:
    """ATLAS should expose its application identity."""
    assert ATLAS_NAME == "ATLAS"
    assert ATLAS_VERSION == "0.7.0"


def test_exit_commands() -> None:
    """ATLAS should recognize supported shutdown commands."""
    assert "exit" in EXIT_COMMANDS
    assert "quit" in EXIT_COMMANDS
    assert "shutdown" in EXIT_COMMANDS
