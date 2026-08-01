"""Tests for the ATLAS core application."""

from pathlib import Path

import pytest

from atlas.conversations.database import (
    SQLiteConversationRepository,
)
from atlas.conversations.service import ConversationService
from atlas.core.app import AtlasApp
from atlas.filesystem.paths import ScopedPathResolver
from atlas.filesystem.service import FileSystemService
from atlas.memory.database import SQLiteMemoryRepository
from atlas.memory.service import MemoryService
from atlas.models.base import ModelProvider
from atlas.permissions.policy import PermissionPolicy
from atlas.permissions.service import PermissionService
from atlas.tools.builtin import (
    CalculatorTool,
    ConfirmationDemoTool,
    CreateDirectoryTool,
    CurrentTimeTool,
    FileInfoTool,
    ListDirectoryTool,
    ReadTextFileTool,
    WriteTextFileTool,
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

    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Record the supplied input and return a response."""
        self.last_input = user_message
        return "Recorded response."


@pytest.fixture
def provider() -> RecordingModelProvider:
    """Create a recording model provider."""
    return RecordingModelProvider()


@pytest.fixture
def workspace(
    tmp_path: Path,
) -> Path:
    """Create an isolated ATLAS file-system workspace."""
    directory = tmp_path / "workspace"
    directory.mkdir()

    return directory


@pytest.fixture
def app(
    tmp_path: Path,
    workspace: Path,
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

    path_resolver = ScopedPathResolver(allowed_directories=(workspace,))

    filesystem_service = FileSystemService(
        path_resolver=path_resolver,
        max_read_bytes=1_000,
        max_write_characters=1_000,
    )

    tool_registry = ToolRegistry()

    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ConfirmationDemoTool())

    tool_registry.register(ListDirectoryTool(filesystem_service))
    tool_registry.register(FileInfoTool(filesystem_service))
    tool_registry.register(ReadTextFileTool(filesystem_service))
    tool_registry.register(CreateDirectoryTool(filesystem_service))
    tool_registry.register(WriteTextFileTool(filesystem_service))

    tool_executor = ToolExecutor(tool_registry)

    permission_service = PermissionService(PermissionPolicy())

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
    """Earlier messages should appear in model input."""
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
    assert "Aerospace Research" in app.process_message("chats")


def test_memory_commands_still_work(
    app: AtlasApp,
) -> None:
    """File-system support should preserve memory commands."""
    response = app.process_message("remember My L2 rocket is named Wraith.")

    assert response.startswith("I will remember that. Memory ID:")


def test_tools_command_lists_filesystem_tools(
    app: AtlasApp,
) -> None:
    """The tools command should list v0.9 tools."""
    response = app.process_message("tools")

    assert "calculator" in response
    assert "current_time" in response
    assert "confirmation_demo" in response
    assert "list_directory" in response
    assert "file_info" in response
    assert "read_text_file" in response
    assert "create_directory" in response
    assert "write_text_file" in response


def test_low_risk_calculator_executes_immediately(
    app: AtlasApp,
) -> None:
    """Low-risk tools should execute immediately."""
    response = app.process_message('tool calculator {"expression": "12 * 4"}')

    assert response == "Tool calculator result: 48"
    assert app.has_pending_tool_request is False


def test_list_directory_executes_immediately(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Directory listing should not require approval."""
    (workspace / "notes.txt").write_text(
        "ATLAS",
        encoding="utf-8",
    )

    response = app.process_message('tool list_directory {"path": "."}')

    assert "Tool list_directory result:" in response
    assert "notes.txt" in response
    assert app.has_pending_tool_request is False


def test_file_info_executes_immediately(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Metadata inspection should not require approval."""
    (workspace / "rocket.txt").write_text(
        "Wraith",
        encoding="utf-8",
    )

    response = app.process_message('tool file_info {"path": "rocket.txt"}')

    assert "Tool file_info result:" in response
    assert "Name: rocket.txt" in response
    assert "Size: 6 bytes" in response
    assert app.has_pending_tool_request is False


def test_read_text_file_executes_immediately(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Reading a scoped text file should be low risk."""
    (workspace / "notes.txt").write_text(
        "Project ATLAS",
        encoding="utf-8",
    )

    response = app.process_message('tool read_text_file {"path": "notes.txt"}')

    assert response == ("Tool read_text_file result: Project ATLAS")
    assert app.has_pending_tool_request is False


def test_read_text_file_rejects_scope_escape(
    app: AtlasApp,
) -> None:
    """ATLAS should prevent path traversal."""
    response = app.process_message('tool read_text_file {"path": "../outside.txt"}')

    assert "Tool input was invalid:" in response
    assert "outside" in response.lower()
    assert app.has_pending_tool_request is False


def test_create_directory_requires_confirmation(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Directory creation should pause before execution."""
    response = app.process_message('tool create_directory {"path": "Rocket Design"}')

    assert "Tool create_directory requires confirmation." in response
    assert app.has_pending_tool_request is True
    assert not (workspace / "Rocket Design").exists()


def test_create_directory_approval_executes_request(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Approval should create the pending directory."""
    app.process_message('tool create_directory {"path": "Rocket Design"}')

    response = app.process_message("confirm yes")

    assert response == ("Tool create_directory result: Created directory: Rocket Design")
    assert (workspace / "Rocket Design").is_dir()
    assert app.has_pending_tool_request is False


def test_create_directory_denial_prevents_change(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Denial should prevent directory creation."""
    app.process_message('tool create_directory {"path": "Denied Directory"}')

    response = app.process_message("confirm no")

    assert response == ("Tool create_directory execution was denied.")
    assert not (workspace / "Denied Directory").exists()
    assert app.has_pending_tool_request is False


def test_write_text_file_requires_confirmation(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Writing a file should pause before execution."""
    response = app.process_message(
        'tool write_text_file {"path": "notes.txt", "content": "Project ATLAS"}'
    )

    assert "Tool write_text_file requires confirmation." in response
    assert not (workspace / "notes.txt").exists()
    assert app.has_pending_tool_request is True


def test_write_text_file_approval_creates_file(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Approval should execute the pending write."""
    app.process_message('tool write_text_file {"path": "notes.txt", "content": "Project ATLAS"}')

    response = app.process_message("confirm yes")

    assert "Created file: notes.txt" in response
    assert (workspace / "notes.txt").read_text(encoding="utf-8") == "Project ATLAS"
    assert app.has_pending_tool_request is False


def test_write_text_file_denial_prevents_file_creation(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """Denied writes should not create files."""
    app.process_message('tool write_text_file {"path": "denied.txt", "content": "Do not write"}')

    response = app.process_message("confirm no")

    assert response == ("Tool write_text_file execution was denied.")
    assert not (workspace / "denied.txt").exists()


def test_medium_risk_tool_rejects_invalid_arguments_before_confirmation(
    app: AtlasApp,
) -> None:
    """Invalid writes should fail before permission checks."""
    response = app.process_message('tool write_text_file {"path": "notes.txt"}')

    assert "Tool input was invalid:" in response
    assert "content" in response
    assert app.has_pending_tool_request is False


def test_tool_rejects_unknown_argument_before_permission(
    app: AtlasApp,
) -> None:
    """Unknown arguments should fail before confirmation."""
    response = app.process_message('tool create_directory {"path": "designs", "unexpected": true}')

    assert "Tool input was invalid:" in response
    assert "Unknown argument" in response
    assert app.has_pending_tool_request is False


def test_invalid_overwrite_type_fails_before_confirmation(
    app: AtlasApp,
) -> None:
    """Invalid boolean arguments should not become pending."""
    response = app.process_message(
        'tool write_text_file {"path": "notes.txt", "content": "ATLAS", "overwrite": "yes"}'
    )

    assert "Tool input was invalid:" in response
    assert "boolean" in response
    assert app.has_pending_tool_request is False


def test_second_pending_request_does_not_replace_first(
    app: AtlasApp,
    workspace: Path,
) -> None:
    """A new request should not overwrite pending state."""
    app.process_message('tool create_directory {"path": "First Directory"}')

    second_response = app.process_message('tool create_directory {"path": "Second Directory"}')

    assert "Another tool request is already awaiting confirmation." in second_response

    app.process_message("confirm yes")

    assert (workspace / "First Directory").is_dir()
    assert not (workspace / "Second Directory").exists()


def test_confirmation_without_pending_request_is_rejected(
    app: AtlasApp,
) -> None:
    """Confirmation should fail when nothing is pending."""
    response = app.process_message("confirm yes")

    assert response == ("There is no pending tool request.")


def test_invalid_confirmation_input_is_rejected(
    app: AtlasApp,
) -> None:
    """Unclear confirmation should not execute."""
    app.process_message('tool create_directory {"path": "Pending Directory"}')

    response = app.process_message("confirm maybe")

    assert response == ("Confirmation must be either 'confirm yes' or 'confirm no'.")
    assert app.has_pending_tool_request is True


def test_invalid_tool_json_is_rejected(
    app: AtlasApp,
) -> None:
    """ATLAS should reject invalid JSON arguments."""
    response = app.process_message("tool calculator not-json")

    assert "Tool arguments must be valid JSON" in response


def test_tool_arguments_must_be_json_object(
    app: AtlasApp,
) -> None:
    """Tool arguments should require an object."""
    response = app.process_message('tool calculator ["2 + 2"]')

    assert response == ("Tool arguments must be a JSON object.")


def test_unknown_tool_is_rejected(
    app: AtlasApp,
) -> None:
    """Unknown tools should be rejected safely."""
    response = app.process_message("tool unknown_tool {}")

    assert "not registered" in response
    assert app.has_pending_tool_request is False
