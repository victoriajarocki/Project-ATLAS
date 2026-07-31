"""Tests for the ATLAS core application."""

from pathlib import Path

import pytest

from atlas.core.app import AtlasApp
from atlas.memory.database import SQLiteMemoryRepository
from atlas.memory.service import MemoryService
from atlas.models.mock import MockModelProvider


@pytest.fixture
def app(tmp_path: Path) -> AtlasApp:
    """Create an isolated ATLAS application for testing."""
    repository = SQLiteMemoryRepository(database_path=tmp_path / "app_memory.db")

    memory_service = MemoryService(repository)
    memory_service.initialize()

    return AtlasApp(
        model_provider=MockModelProvider(),
        memory_service=memory_service,
    )


def test_app_uses_model_provider(app: AtlasApp) -> None:
    """ATLAS Core should send messages to its provider."""
    response = app.process_message("Test message")

    assert response == "Mock response to: Test message"


def test_app_handles_empty_messages(app: AtlasApp) -> None:
    """ATLAS Core should safely handle empty input."""
    response = app.process_message("   ")

    assert response == "I did not receive a message."


def test_app_reports_provider_name(app: AtlasApp) -> None:
    """ATLAS Core should expose its provider name."""
    assert app.provider_name == "Mock"


def test_app_reports_memory_status(app: AtlasApp) -> None:
    """ATLAS Core should report persistent memory status."""
    assert app.memory_enabled is True


def test_remember_command_saves_memory(
    app: AtlasApp,
) -> None:
    """The remember command should save information."""
    response = app.process_message("remember My L2 rocket is named Wraith.")

    assert response.startswith("I will remember that. Memory ID:")


def test_memories_command_lists_saved_memory(
    app: AtlasApp,
) -> None:
    """The memories command should display saved memories."""
    app.process_message("remember My L2 rocket is named Wraith.")

    response = app.process_message("memories")

    assert "Persistent memories:" in response
    assert "Wraith" in response


def test_forget_command_deletes_memory(
    app: AtlasApp,
) -> None:
    """The forget command should delete selected memory."""
    saved_response = app.process_message("remember Delete this information.")

    memory_id = int(
        saved_response.removeprefix("I will remember that. Memory ID: ").removesuffix(".")
    )

    deleted_response = app.process_message(f"forget {memory_id}")

    assert deleted_response == (f"Memory {memory_id} was deleted.")


def test_invalid_forget_command_is_rejected(
    app: AtlasApp,
) -> None:
    """The forget command should require a numeric ID."""
    response = app.process_message("forget banana")

    assert response == ("Use a numeric memory ID, such as: forget 3")
