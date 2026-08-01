"""Tests for the ATLAS tool and plugin framework."""

import pytest

from atlas.tools.base import (
    ToolNotFoundError,
    ToolRiskLevel,
    ToolValidationError,
)
from atlas.tools.builtin import (
    CalculatorTool,
    ConfirmationDemoTool,
    CurrentTimeTool,
)
from atlas.tools.executor import ToolExecutor
from atlas.tools.registry import ToolRegistry


@pytest.fixture
def registry() -> ToolRegistry:
    """Create a registry containing built-in tools."""
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ConfirmationDemoTool())

    return tool_registry


@pytest.fixture
def executor(
    registry: ToolRegistry,
) -> ToolExecutor:
    """Create an executor containing built-in tools."""
    return ToolExecutor(registry)


def test_registry_contains_registered_tool(
    registry: ToolRegistry,
) -> None:
    """Registered tools should be discoverable."""
    assert registry.contains("calculator")
    assert registry.contains("CALCULATOR")
    assert registry.contains("current_time")
    assert registry.contains("confirmation_demo")


def test_registry_lists_registered_tools(
    registry: ToolRegistry,
) -> None:
    """The registry should list all built-in tool definitions."""
    definitions = registry.list_definitions()
    names = [definition.name for definition in definitions]

    assert names == [
        "calculator",
        "confirmation_demo",
        "current_time",
    ]


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
        arguments={"expression": "2 + 3 * 4"},
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
        arguments={"expression": "(2 + 3) * 4"},
    )

    assert result.success is True
    assert result.output == "20"


def test_calculator_rejects_missing_expression(
    executor: ToolExecutor,
) -> None:
    """The calculator should require an expression."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="calculator",
            arguments={},
        )


def test_calculator_rejects_non_string_expression(
    executor: ToolExecutor,
) -> None:
    """The calculator should reject non-string expressions."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="calculator",
            arguments={"expression": 123},
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
            arguments={"expression": "1 / 0"},
        )


def test_current_time_definition_is_low_risk(
    registry: ToolRegistry,
) -> None:
    """The current-time tool should be classified as low risk."""
    tool = registry.get("current_time")

    assert tool.definition.risk_level is ToolRiskLevel.LOW
    assert tool.definition.requires_confirmation is False


def test_current_time_rejects_arguments(
    executor: ToolExecutor,
) -> None:
    """The current-time tool should accept no arguments."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="current_time",
            arguments={"timezone": "UTC"},
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
    """The demonstration tool should return its validated message."""
    result = executor.execute(
        tool_name="confirmation_demo",
        arguments={"message": "Approved action"},
    )

    assert result.success is True
    assert result.tool_name == "confirmation_demo"
    assert result.output == "Approved action"
    assert result.error is None


def test_confirmation_demo_strips_message_whitespace(
    executor: ToolExecutor,
) -> None:
    """The demonstration tool should clean message whitespace."""
    result = executor.execute(
        tool_name="confirmation_demo",
        arguments={"message": "  Approved action  "},
    )

    assert result.output == "Approved action"


def test_confirmation_demo_rejects_missing_message(
    executor: ToolExecutor,
) -> None:
    """The demonstration tool should require a message."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="confirmation_demo",
            arguments={},
        )


def test_confirmation_demo_rejects_empty_message(
    executor: ToolExecutor,
) -> None:
    """The demonstration tool should reject empty messages."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="confirmation_demo",
            arguments={"message": "   "},
        )


def test_confirmation_demo_rejects_non_string_message(
    executor: ToolExecutor,
) -> None:
    """The demonstration tool should reject non-string messages."""
    with pytest.raises(ToolValidationError):
        executor.execute(
            tool_name="confirmation_demo",
            arguments={"message": 123},
        )
