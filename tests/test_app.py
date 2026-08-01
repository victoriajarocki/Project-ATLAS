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
from atlas.permissions.policy import PermissionPolicy
from atlas.permissions.service import PermissionService
from atlas.tools.builtin import (
    CalculatorTool,
    ConfirmationDemoTool,
    CurrentTimeTool,
)
from atlas.tools.executor import ToolExecutor
from atlas.tools.registry import ToolRegistry


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

    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ConfirmationDemoTool())

    tool_executor = ToolExecutor(tool_registry)

    permission_policy = PermissionPolicy()
    permission_service = PermissionService(permission_policy)

    return AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
        conversation_service=conversation_service,
        tool_executor=tool_executor,
        permission_service=permission_service,
    )


def test_app_reports_subsystem_status(
    app: AtlasApp,
) -> None:
    """ATLAS should report enabled subsystems."""
    assert app.provider_name == "Recording"
    assert app.memory_enabled is True
    assert app.conversations_enabled is True
    assert app.tools_enabled is True
    assert app.permissions_enabled is True
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
    """Permission support should preserve memory commands."""
    response = app.process_message("remember My L2 rocket is named Wraith.")

    assert response.startswith("I will remember that. Memory ID:")


def test_tools_command_lists_registered_tools(
    app: AtlasApp,
) -> None:
    """The tools command should list available tools."""
    response = app.process_message("tools")

    assert "Registered tools:" in response
    assert "calculator" in response
    assert "current_time" in response
    assert "confirmation_demo" in response


def test_low_risk_calculator_executes_immediately(
    app: AtlasApp,
) -> None:
    """Low-risk tools should execute without confirmation."""
    response = app.process_message('tool calculator {"expression": "12 * 4"}')

    assert response == "Tool calculator result: 48"
    assert app.has_pending_tool_request is False


def test_current_time_executes_immediately(
    app: AtlasApp,
) -> None:
    """The low-risk current-time tool should execute immediately."""
    response = app.process_message("tool current_time {}")

    assert response.startswith("Tool current_time result:")
    assert app.has_pending_tool_request is False


def test_medium_risk_tool_waits_for_confirmation(
    app: AtlasApp,
) -> None:
    """Medium-risk tools should pause before execution."""
    response = app.process_message('tool confirmation_demo {"message": "Approved action"}')

    assert "Tool confirmation_demo requires confirmation." in response
    assert "Risk level: medium." in response
    assert "confirm yes" in response
    assert "confirm no" in response
    assert app.has_pending_tool_request is True


def test_confirmation_approval_executes_pending_tool(
    app: AtlasApp,
) -> None:
    """Approval should execute the pending tool."""
    request_response = app.process_message(
        'tool confirmation_demo {"message": "Permission granted"}'
    )

    assert "requires confirmation" in request_response
    assert app.has_pending_tool_request is True

    confirmation_response = app.process_message("confirm yes")

    assert confirmation_response == ("Tool confirmation_demo result: Permission granted")
    assert app.has_pending_tool_request is False


def test_confirmation_denial_blocks_pending_tool(
    app: AtlasApp,
) -> None:
    """Denial should clear the request without execution."""
    app.process_message('tool confirmation_demo {"message": "Do not execute"}')

    assert app.has_pending_tool_request is True

    response = app.process_message("confirm no")

    assert response == ("Tool confirmation_demo execution was denied.")
    assert app.has_pending_tool_request is False


def test_confirmation_without_pending_request_is_rejected(
    app: AtlasApp,
) -> None:
    """Confirmation should fail safely when nothing is pending."""
    response = app.process_message("confirm yes")

    assert response == "There is no pending tool request."
    assert app.has_pending_tool_request is False


def test_invalid_confirmation_input_is_rejected(
    app: AtlasApp,
) -> None:
    """Unclear confirmation input should not execute a tool."""
    app.process_message('tool confirmation_demo {"message": "Pending action"}')

    response = app.process_message("confirm maybe")

    assert response == ("Confirmation must be either 'confirm yes' or 'confirm no'.")
    assert app.has_pending_tool_request is True


def test_second_pending_request_does_not_replace_first(
    app: AtlasApp,
) -> None:
    """A second request should not overwrite pending state."""
    first_response = app.process_message('tool confirmation_demo {"message": "First action"}')

    assert "requires confirmation" in first_response
    assert app.has_pending_tool_request is True

    second_response = app.process_message('tool confirmation_demo {"message": "Second action"}')

    assert "Another tool request is already awaiting confirmation." in second_response

    confirmation_response = app.process_message("confirm yes")

    assert confirmation_response == ("Tool confirmation_demo result: First action")
    assert app.has_pending_tool_request is False


def test_invalid_tool_json_is_rejected(
    app: AtlasApp,
) -> None:
    """ATLAS should reject invalid JSON arguments."""
    response = app.process_message("tool calculator not-json")

    assert "Tool arguments must be valid JSON" in response


def test_tool_arguments_must_be_json_object(
    app: AtlasApp,
) -> None:
    """Tool arguments should require a JSON object."""
    response = app.process_message('tool calculator ["2 + 2"]')

    assert response == ("Tool arguments must be a JSON object.")


def test_unknown_tool_is_rejected(
    app: AtlasApp,
) -> None:
    """Unknown tools should not reach permission evaluation."""
    response = app.process_message("tool unknown_tool {}")

    assert "not registered" in response
    assert app.has_pending_tool_request is False
