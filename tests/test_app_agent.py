"""Integration tests for the ATLAS agent application workflow."""

from collections.abc import Iterator
from pathlib import Path

import pytest

from atlas.agent.exceptions import (
    AgentDecisionError,
    AgentParsingError,
)
from atlas.agent.parser import AgentDecisionParser
from atlas.agent.prompt import AgentPromptBuilder
from atlas.agent.service import AgentService
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


class ScriptedModelProvider(ModelProvider):
    """Return predefined model outputs in sequence."""

    def __init__(
        self,
        responses: list[str],
    ) -> None:
        """Initialize the scripted provider."""
        self._responses: Iterator[str] = iter(responses)
        self.inputs: list[str] = []

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Scripted"

    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Record model input and return the next response."""
        self.inputs.append(user_message)

        try:
            return next(self._responses)
        except StopIteration as error:
            raise RuntimeError("No scripted model response remains.") from error


def create_agent_app(
    tmp_path: Path,
    responses: list[str],
) -> tuple[
    AtlasApp,
    ScriptedModelProvider,
    Path,
]:
    """Create an isolated agent-enabled ATLAS application."""
    database_path = tmp_path / "atlas_agent_test.db"
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    provider = ScriptedModelProvider(responses)

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

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(ConfirmationDemoTool())
    registry.register(ListDirectoryTool(filesystem_service))
    registry.register(FileInfoTool(filesystem_service))
    registry.register(ReadTextFileTool(filesystem_service))
    registry.register(CreateDirectoryTool(filesystem_service))
    registry.register(WriteTextFileTool(filesystem_service))

    executor = ToolExecutor(registry)
    permission_service = PermissionService(PermissionPolicy())

    agent_service = AgentService(
        model_provider=provider,
        prompt_builder=AgentPromptBuilder(registry),
        decision_parser=AgentDecisionParser(),
        tool_executor=executor,
        permission_service=permission_service,
    )

    app = AtlasApp(
        model_provider=provider,
        memory_service=memory_service,
        conversation_service=conversation_service,
        tool_executor=executor,
        permission_service=permission_service,
        agent_service=agent_service,
    )

    return app, provider, workspace


def test_app_reports_agent_enabled(
    tmp_path: Path,
) -> None:
    """The application should report agent availability."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=[],
    )

    assert app.agent_enabled is True


def test_agent_returns_direct_response(
    tmp_path: Path,
) -> None:
    """A direct model decision should reach the user."""
    app, provider, _ = create_agent_app(
        tmp_path,
        responses=[('{"decision":"respond","response":"Hello from ATLAS."}')],
    )

    response = app.process_message("Hello.")

    assert response == "Hello from ATLAS."
    assert len(provider.inputs) == 1
    assert "CURRENT USER REQUEST" in provider.inputs[0]
    assert "Hello." in provider.inputs[0]


def test_agent_automatically_uses_calculator(
    tmp_path: Path,
) -> None:
    """Natural language should trigger calculator execution."""
    app, provider, _ = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"calculator","arguments":'
                '{"expression":"347 * 982"}}}'
            )
        ],
    )

    response = app.process_message("What is 347 multiplied by 982?")

    assert response == "340754"
    assert len(provider.inputs) == 1
    assert "AVAILABLE TOOLS" in provider.inputs[0]
    assert '"name": "calculator"' in provider.inputs[0]


def test_agent_automatically_reads_text_file(
    tmp_path: Path,
) -> None:
    """The agent should use the scoped file-reading tool."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"read_text_file","arguments":'
                '{"path":"Rocket Design/notes.txt"}}}'
            )
        ],
    )

    rocket_directory = workspace / "Rocket Design"
    rocket_directory.mkdir()

    (rocket_directory / "notes.txt").write_text(
        "Project Wraith",
        encoding="utf-8",
    )

    response = app.process_message("Read my Rocket Design notes.")

    assert response == "Project Wraith"
    assert len(provider.inputs) == 1


def test_agent_automatically_lists_directory(
    tmp_path: Path,
) -> None:
    """The agent should list a configured workspace."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[
            ('{"decision":"use_tool","tool":{"name":"list_directory","arguments":{"path":"."}}}')
        ],
    )

    (workspace / "notes.txt").write_text(
        "ATLAS",
        encoding="utf-8",
    )

    response = app.process_message("What files are in my workspace?")

    assert response == "file: notes.txt (size: 5 bytes)"
    assert len(provider.inputs) == 1


def test_agent_medium_risk_action_requires_confirmation(
    tmp_path: Path,
) -> None:
    """A model-selected state change should pause."""
    app, _, workspace = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"create_directory","arguments":'
                '{"path":"Rocket Design"}}}'
            )
        ],
    )

    response = app.process_message("Create a Rocket Design folder.")

    assert "Tool create_directory requires confirmation." in response
    assert app.has_pending_tool_request is True
    assert not (workspace / "Rocket Design").exists()


def test_confirm_yes_completes_agent_action(
    tmp_path: Path,
) -> None:
    """Approval should resume a model-selected action."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"create_directory","arguments":'
                '{"path":"Rocket Design"}}}'
            )
        ],
    )

    initial_response = app.process_message("Create a Rocket Design folder.")

    assert "requires confirmation" in initial_response
    assert not (workspace / "Rocket Design").exists()

    final_response = app.process_message("confirm yes")

    assert final_response == ("Created directory: Rocket Design")
    assert (workspace / "Rocket Design").is_dir()
    assert app.has_pending_tool_request is False
    assert len(provider.inputs) == 1


def test_confirm_no_denies_agent_action(
    tmp_path: Path,
) -> None:
    """Denial should prevent a routed state change."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[],
    )

    app.process_message("Create a folder called Denied Folder.")

    response = app.process_message("confirm no")

    assert response == ("Tool create_directory execution was denied.")
    assert not (workspace / "Denied Folder").exists()
    assert app.has_pending_tool_request is False
    assert provider.inputs == []


def test_agent_write_file_requires_confirmation(
    tmp_path: Path,
) -> None:
    """A model-selected file write should pause."""
    app, _, workspace = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"write_text_file","arguments":'
                '{"path":"notes.txt",'
                '"content":"Project ATLAS"}}}'
            )
        ],
    )

    response = app.process_message("Write Project ATLAS into notes.txt.")

    assert "Tool write_text_file requires confirmation." in response
    assert not (workspace / "notes.txt").exists()


def test_agent_write_file_executes_after_approval(
    tmp_path: Path,
) -> None:
    """Approved model-selected writes should execute."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[
            (
                '{"decision":"use_tool","tool":'
                '{"name":"write_text_file","arguments":'
                '{"path":"notes.txt",'
                '"content":"Project ATLAS"}}}'
            )
        ],
    )

    app.process_message("Write Project ATLAS into notes.txt.")

    response = app.process_message("confirm yes")

    assert response == ("Created file: notes.txt (13 characters)")
    assert (workspace / "notes.txt").read_text(encoding="utf-8") == "Project ATLAS"
    assert len(provider.inputs) == 1


def test_deterministic_file_creation_requires_confirmation(
    tmp_path: Path,
) -> None:
    """Recognized file creation should bypass model discretion."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[],
    )

    response = app.process_message("Create a file called hello.txt that says Hello World.")

    assert "Tool write_text_file requires confirmation." in response
    assert app.has_pending_tool_request is True
    assert not (workspace / "hello.txt").exists()
    assert provider.inputs == []


def test_deterministic_file_creation_executes_after_approval(
    tmp_path: Path,
) -> None:
    """Approved routed file creation should write the file."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[],
    )

    app.process_message("Create a file called hello.txt that says Hello World.")

    response = app.process_message("confirm yes")

    assert response == ("Created file: hello.txt (11 characters)")
    assert (workspace / "hello.txt").read_text(encoding="utf-8") == "Hello World"
    assert app.has_pending_tool_request is False
    assert provider.inputs == []


def test_pending_agent_request_blocks_new_message(
    tmp_path: Path,
) -> None:
    """A pending routed action should block unrelated requests."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[],
    )

    app.process_message("Create a folder called First Folder.")

    response = app.process_message("What time is it?")

    assert response == (
        "A tool request is awaiting confirmation. "
        "Use 'confirm yes' or 'confirm no' before "
        "submitting another request."
    )
    assert provider.inputs == []
    assert not (workspace / "First Folder").exists()


def test_explicit_tool_command_still_works(
    tmp_path: Path,
) -> None:
    """Legacy explicit tool commands should remain supported."""
    app, provider, _ = create_agent_app(
        tmp_path,
        responses=[],
    )

    response = app.process_message('tool calculator {"expression": "12 * 4"}')

    assert response == "Tool calculator result: 48"
    assert provider.inputs == []


def test_explicit_medium_risk_tool_still_uses_confirmation(
    tmp_path: Path,
) -> None:
    """Explicit medium-risk commands should remain compatible."""
    app, provider, workspace = create_agent_app(
        tmp_path,
        responses=[],
    )

    response = app.process_message('tool create_directory {"path": "Explicit Folder"}')

    assert "Tool create_directory requires confirmation." in response
    assert app.has_pending_tool_request is True
    assert provider.inputs == []

    approval_response = app.process_message("confirm yes")

    assert approval_response == ("Tool create_directory result: Created directory: Explicit Folder")
    assert (workspace / "Explicit Folder").is_dir()


def test_agent_rejects_invalid_model_json(
    tmp_path: Path,
) -> None:
    """Malformed model output should fail safely."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=["not valid JSON"],
    )

    with pytest.raises(
        AgentParsingError,
        match="not valid JSON",
    ):
        app.process_message("Hello.")


def test_agent_rejects_hallucinated_tool(
    tmp_path: Path,
) -> None:
    """An unregistered model-selected tool should fail."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=[('{"decision":"use_tool","tool":{"name":"run_shell","arguments":{}}}')],
    )

    with pytest.raises(
        AgentDecisionError,
        match="unavailable tool",
    ):
        app.process_message("Run a terminal command.")


def test_agent_rejects_invalid_tool_arguments(
    tmp_path: Path,
) -> None:
    """Malformed generated arguments should fail safely."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=[('{"decision":"use_tool","tool":{"name":"calculator","arguments":{}}}')],
    )

    with pytest.raises(
        AgentDecisionError,
        match="invalid arguments",
    ):
        app.process_message("Calculate something.")


def test_direct_agent_response_is_stored_in_history(
    tmp_path: Path,
) -> None:
    """Direct responses should persist in the conversation."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=[('{"decision":"respond","response":"Stored agent response."}')],
    )

    app.process_message("Store this interaction.")

    history = app.process_message("history")

    assert "User: Store this interaction." in history
    assert "Assistant: Stored agent response." in history


def test_confirmed_agent_response_is_stored_in_history(
    tmp_path: Path,
) -> None:
    """Final confirmed responses should be persisted."""
    app, _, _ = create_agent_app(
        tmp_path,
        responses=[],
    )

    app.process_message("Create a folder called Stored Folder.")
    app.process_message("confirm yes")

    history = app.process_message("history")

    assert "User: Create a folder called Stored Folder." in history
    assert "Assistant: Created directory: Stored Folder" in history


def test_agent_receives_previous_conversation_context(
    tmp_path: Path,
) -> None:
    """Stored conversation history should reach the agent."""
    app, provider, _ = create_agent_app(
        tmp_path,
        responses=[
            ('{"decision":"respond","response":"I will remember the name."}'),
            ('{"decision":"respond","response":"The rocket is Specter."}'),
        ],
    )

    app.process_message("My experimental rocket is named Specter.")

    response = app.process_message("What is my experimental rocket named?")

    assert response == "The rocket is Specter."
    assert len(provider.inputs) == 2
    assert "My experimental rocket is named Specter." in provider.inputs[1]
    assert "I will remember the name." in provider.inputs[1]
