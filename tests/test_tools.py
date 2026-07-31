"""Tests for the ATLAS tool and plugin framework."""

import pytest

from atlas.tools.base import (
    ToolNotFoundError,
    ToolValidationError,
)
from atlas.tools.builtin import (
    CalculatorTool,
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


def test_calculator_addition(
    executor: ToolExecutor,
) -> None:
    """The calculator should evaluate arithmetic."""
    result = executor.execute(
        tool_name="calculator",
        arguments={"expression": "2 + 3 * 4"},
    )

    assert result.success is True
    assert result.output == "14"


def test_calculator_parentheses(
    executor: ToolExecutor,
) -> None:
    """The calculator should respect parentheses."""
    result = executor.execute(
        tool_name="calculator",
        arguments={"expression": "(2 + 3) * 4"},
    )

    assert result.output == "20"


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
    assert result.output
