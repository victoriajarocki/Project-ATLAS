"""Tests for the ATLAS tool and plugin framework."""

from pathlib import Path

import pytest

from atlas.filesystem.paths import ScopedPathResolver
from atlas.filesystem.service import FileSystemService
from atlas.tools.base import (
    ToolNotFoundError,
    ToolRiskLevel,
    ToolValidationError,
)
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


@pytest.fixture
def workspace(
    tmp_path: Path,
) -> Path:
    """Create an isolated file-system workspace."""
    directory = tmp_path / "workspace"
    directory.mkdir()

    return directory


@pytest.fixture
def filesystem_service(
    workspace: Path,
) -> FileSystemService:
    """Create a scoped file-system service."""
    resolver = ScopedPathResolver(allowed_directories=(workspace,))

    return FileSystemService(
        path_resolver=resolver,
        max_read_bytes=1_000,
        max_write_characters=1_000,
    )


@pytest.fixture
def registry(
    filesystem_service: FileSystemService,
) -> ToolRegistry:
    """Create a registry containing all built-in tools."""
    tool_registry = ToolRegistry()

    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ConfirmationDemoTool())

    tool_registry.register(ListDirectoryTool(filesystem_service))
    tool_registry.register(FileInfoTool(filesystem_service))
    tool_registry.register(ReadTextFileTool(filesystem_service))
    tool_registry.register(CreateDirectoryTool(filesystem_service))
    tool_registry.register(WriteTextFileTool(filesystem_service))

    return tool_registry


@pytest.fixture
def executor(
    registry: ToolRegistry,
) -> ToolExecutor:
    """Create an executor containing all built-in tools."""
    return ToolExecutor(registry)


def test_registry_contains_registered_tools(
    registry: ToolRegistry,
) -> None:
    """Registered tools should be discoverable."""
    expected_names = {
        "calculator",
        "confirmation_demo",
        "create_directory",
        "current_time",
        "file_info",
        "list_directory",
        "read_text_file",
        "write_text_file",
    }

    for name in expected_names:
        assert registry.contains(name)

    assert registry.contains("CALCULATOR")


def test_registry_lists_all_registered_tools(
    registry: ToolRegistry,
) -> None:
    """The registry should list every built-in definition."""
    definitions = registry.list_definitions()
    names = {definition.name for definition in definitions}

    assert names == {
        "calculator",
        "confirmation_demo",
        "create_directory",
        "current_time",
        "file_info",
        "list_directory",
        "read_text_file",
        "write_text_file",
    }


def test_registry_rejects_duplicate_tool(
    registry: ToolRegistry,
) -> None:
    """Duplicate tool names should be rejected."""
    with pytest.raises(ValueError):
        registry.register(CalculatorTool())


def test_registry_rejects_unknown_tool(
    registry: ToolRegistry,
) -> None:
    """Unknown tools should raise a tool error."""
    with pytest.raises(ToolNotFoundError):
        registry.get("unknown")


def test_calculator_definition_is_low_risk(
    registry: ToolRegistry,
) -> None:
    """The calculator should be classified as low risk."""
    tool = registry.get("calculator")

    assert tool.definition.risk_level is ToolRiskLevel.LOW
    assert tool.definition.requires_confirmation is False


def test_calculator_addition(
    executor: ToolExecutor,
) -> None:
    """The calculator should evaluate arithmetic."""
    result = executor.execute(
        tool_name="calculator",
        arguments={
            "expression": "2 + 3 * 4",
        },
    )

    assert result.success is True
    assert result.tool_name == "calculator"
    assert result.output == "14"
    assert result.error is None


def test_calculator_parentheses(
    executor: ToolExecutor,
) -> None:
    """The calculator should respect parentheses."""
    result = executor.execute(
        tool_name="calculator",
        arguments={
            "expression": "(2 + 3) * 4",
        },
    )

    assert result.success is True
    assert result.output == "20"


def test_calculator_rejects_missing_expression(
    executor: ToolExecutor,
) -> None:
    """The calculator should require an expression."""
    with pytest.raises(
        ToolValidationError,
        match="Missing required argument",
    ):
        executor.execute(
            tool_name="calculator",
            arguments={},
        )


def test_calculator_rejects_non_string_expression(
    executor: ToolExecutor,
) -> None:
    """The calculator should reject non-string expressions."""
    with pytest.raises(
        ToolValidationError,
        match="must be of type string",
    ):
        executor.execute(
            tool_name="calculator",
            arguments={
                "expression": 123,
            },
        )


def test_calculator_rejects_unknown_argument(
    executor: ToolExecutor,
) -> None:
    """The shared validator should reject unknown keys."""
    with pytest.raises(
        ToolValidationError,
        match="Unknown argument",
    ):
        executor.execute(
            tool_name="calculator",
            arguments={
                "expression": "2 + 2",
                "unexpected": True,
            },
        )


def test_calculator_rejects_code_execution(
    executor: ToolExecutor,
) -> None:
    """The calculator should reject Python code."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="calculator",
            arguments={"expression": ("__import__('os').system('echo unsafe')")},
        )


def test_calculator_rejects_division_by_zero(
    executor: ToolExecutor,
) -> None:
    """The calculator should reject invalid arithmetic."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="calculator",
            arguments={
                "expression": "1 / 0",
            },
        )


def test_current_time_definition_is_low_risk(
    registry: ToolRegistry,
) -> None:
    """The current-time tool should be low risk."""
    tool = registry.get("current_time")

    assert tool.definition.risk_level is ToolRiskLevel.LOW
    assert tool.definition.requires_confirmation is False


def test_current_time_rejects_arguments(
    executor: ToolExecutor,
) -> None:
    """The current-time tool should accept no arguments."""
    with pytest.raises(
        ToolValidationError,
        match="Unknown argument",
    ):
        executor.execute(
            tool_name="current_time",
            arguments={
                "timezone": "UTC",
            },
        )


def test_current_time_returns_result(
    executor: ToolExecutor,
) -> None:
    """The current-time tool should return text."""
    result = executor.execute(
        tool_name="current_time",
        arguments={},
    )

    assert result.success is True
    assert result.tool_name == "current_time"
    assert result.output
    assert result.error is None


def test_confirmation_demo_requires_confirmation(
    registry: ToolRegistry,
) -> None:
    """The demonstration tool should require confirmation."""
    tool = registry.get("confirmation_demo")

    assert tool.definition.risk_level is ToolRiskLevel.MEDIUM
    assert tool.definition.requires_confirmation is True


def test_confirmation_demo_accepts_valid_message(
    executor: ToolExecutor,
) -> None:
    """The demonstration tool should return its message."""
    result = executor.execute(
        tool_name="confirmation_demo",
        arguments={
            "message": "Approved action",
        },
    )

    assert result.success is True
    assert result.output == "Approved action"


def test_list_directory_is_low_risk(
    registry: ToolRegistry,
) -> None:
    """Directory listing should execute without confirmation."""
    tool = registry.get("list_directory")

    assert tool.definition.risk_level is ToolRiskLevel.LOW
    assert tool.definition.requires_confirmation is False


def test_list_directory_returns_workspace_entries(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """The listing tool should return scoped entries."""
    (workspace / "documents").mkdir()
    (workspace / "notes.txt").write_text(
        "ATLAS",
        encoding="utf-8",
    )

    result = executor.execute(
        tool_name="list_directory",
        arguments={
            "path": ".",
        },
    )

    assert result.success is True
    assert "documents" in result.output
    assert "notes.txt" in result.output


def test_list_directory_defaults_to_workspace_root(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """The path argument should be optional."""
    (workspace / "example.txt").write_text(
        "Example",
        encoding="utf-8",
    )

    result = executor.execute(
        tool_name="list_directory",
        arguments={},
    )

    assert "example.txt" in result.output


def test_file_info_returns_metadata(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """The metadata tool should describe a scoped file."""
    (workspace / "rocket.txt").write_text(
        "Wraith",
        encoding="utf-8",
    )

    result = executor.execute(
        tool_name="file_info",
        arguments={
            "path": "rocket.txt",
        },
    )

    assert result.success is True
    assert "Name: rocket.txt" in result.output
    assert "Type: file" in result.output
    assert "Size: 6 bytes" in result.output


def test_read_text_file_returns_contents(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """The read tool should return UTF-8 text."""
    (workspace / "notes.txt").write_text(
        "Project ATLAS",
        encoding="utf-8",
    )

    result = executor.execute(
        tool_name="read_text_file",
        arguments={
            "path": "notes.txt",
        },
    )

    assert result.success is True
    assert result.output == "Project ATLAS"


def test_read_text_file_rejects_scope_escape(
    executor: ToolExecutor,
) -> None:
    """The read tool should reject parent traversal."""
    with pytest.raises(
        ToolValidationError,
        match="outside",
    ):
        executor.execute(
            tool_name="read_text_file",
            arguments={
                "path": "../outside.txt",
            },
        )


def test_create_directory_is_medium_risk(
    registry: ToolRegistry,
) -> None:
    """Directory creation should require confirmation."""
    tool = registry.get("create_directory")

    assert tool.definition.risk_level is ToolRiskLevel.MEDIUM
    assert tool.definition.requires_confirmation is True


def test_create_directory_executes_valid_request(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """Direct executor use should create a directory."""
    result = executor.execute(
        tool_name="create_directory",
        arguments={
            "path": "Rocket Design",
        },
    )

    assert result.success is True
    assert (workspace / "Rocket Design").is_dir()
    assert result.output == "Created directory: Rocket Design"


def test_write_text_file_is_medium_risk(
    registry: ToolRegistry,
) -> None:
    """Text writing should require confirmation."""
    tool = registry.get("write_text_file")

    assert tool.definition.risk_level is ToolRiskLevel.MEDIUM
    assert tool.definition.requires_confirmation is True


def test_write_text_file_creates_file(
    executor: ToolExecutor,
    workspace: Path,
) -> None:
    """Direct executor use should write a UTF-8 file."""
    result = executor.execute(
        tool_name="write_text_file",
        arguments={
            "path": "notes.txt",
            "content": "Project ATLAS",
        },
    )

    assert result.success is True
    assert (workspace / "notes.txt").read_text(encoding="utf-8") == "Project ATLAS"
    assert "Created file: notes.txt" in result.output


def test_write_text_file_rejects_invalid_overwrite_type(
    executor: ToolExecutor,
) -> None:
    """The shared validator should enforce booleans."""
    with pytest.raises(
        ToolValidationError,
        match="must be of type boolean",
    ):
        executor.execute(
            tool_name="write_text_file",
            arguments={
                "path": "notes.txt",
                "content": "ATLAS",
                "overwrite": "yes",
            },
        )


def test_write_text_file_rejects_missing_content(
    executor: ToolExecutor,
) -> None:
    """The write tool should require content."""
    with pytest.raises(
        ToolValidationError,
        match="Missing required argument",
    ):
        executor.execute(
            tool_name="write_text_file",
            arguments={
                "path": "notes.txt",
            },
        )
