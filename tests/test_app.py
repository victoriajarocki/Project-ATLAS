"""Tests for the ATLAS core application."""

from pathlib import Path

import pytest

from atlas.conversations.database import (
    SQLiteConversationRepository,
)
from atlas.conversations.service import ConversationService
from atlas.core.app import AtlasApp
from atlas.memory.database import SQLiteMemoryRepository
from atlas.memory.service import MemoryService
from atlas.models.base import ModelProvider


class RecordingModelProvider(ModelProvider):
    """Record model input while returning a fixed response."""

    def __init__(self) -> None:
        """Initialize the recording provider."""
        self.last_input = ""

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Recording"

    def generate_response(self, user_message: str) -> str:
        """Record the supplied input and return a response."""
        self.last_input = user_message
        return "Recorded response."


@pytest.fixture
def provider() -> RecordingModelProvider:
    """Create a recording model provider."""
    return RecordingModelProvider()


@pytest.fixture
def app(
    tmp_path: Path,
    provider: RecordingModelProvider,
) -> AtlasApp:
    """Create an isolated ATLAS application."""
    database_path = tmp_path / "atlas_test.db"

    memory_repository = SQLiteMemoryRepository(database_path=database_path)
    memory_service = MemoryService(memory_repository)
    memory_service.initialize()

    conversation_repository = SQLiteConversationRepository(database_path=database_path)
    conversation_service = ConversationService(conversation_repository)
    conversation_service.initialize()

    return AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
        conversation_service=conversation_service,
    )


def test_app_reports_subsystem_status(
    app: AtlasApp,
) -> None:
    """ATLAS should report enabled subsystems."""
    assert app.provider_name == "Recording"
    assert app.memory_enabled is True
    assert app.conversations_enabled is True
    assert app.active_conversation_id is not None


def test_normal_messages_are_stored(
    app: AtlasApp,
) -> None:
    """Normal user and assistant messages should be stored."""
    app.process_message("Hello ATLAS.")

    history = app.process_message("history")

    assert "User: Hello ATLAS." in history
    assert "Assistant: Recorded response." in history


def test_previous_messages_are_sent_as_context(
    app: AtlasApp,
    provider: RecordingModelProvider,
) -> None:
    """Earlier messages should appear in later model input."""
    app.process_message("My experimental rocket is called Specter.")

    app.process_message("What is its name?")

    assert "User: My experimental rocket is called Specter." in provider.last_input
    assert "Assistant: Recorded response." in provider.last_input
    assert "User: What is its name?" in provider.last_input


def test_new_chat_changes_active_conversation(
    app: AtlasApp,
) -> None:
    """The new-chat command should activate a new chat."""
    original_id = app.active_conversation_id

    response = app.process_message("new chat Rocket Planning")

    assert response.startswith("Created chat ")
    assert app.active_conversation_id != original_id


def test_chats_lists_conversations(
    app: AtlasApp,
) -> None:
    """The chats command should list saved chats."""
    app.process_message("new chat First")
    app.process_message("new chat Second")

    response = app.process_message("chats")

    assert "Saved conversations:" in response
    assert "First" in response
    assert "Second" in response


def test_use_chat_switches_conversation(
    app: AtlasApp,
) -> None:
    """ATLAS should switch between existing chats."""
    original_id = app.active_conversation_id
    app.process_message("new chat Another Chat")

    assert original_id is not None

    response = app.process_message(f"use chat {original_id}")

    assert response.startswith(f"Switched to chat {original_id}:")
    assert app.active_conversation_id == original_id


def test_rename_chat_changes_title(
    app: AtlasApp,
) -> None:
    """The active conversation should be renameable."""
    response = app.process_message("rename chat Aerospace Research")

    assert "Aerospace Research" in response

    chats = app.process_message("chats")

    assert "Aerospace Research" in chats


def test_memory_commands_still_work(
    app: AtlasApp,
) -> None:
    """Conversation support should preserve memory commands."""
    response = app.process_message("remember My L2 rocket is named Wraith.")

    assert response.startswith("I will remember that. Memory ID:")
