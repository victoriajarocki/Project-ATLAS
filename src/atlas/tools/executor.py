"""Controlled execution service for ATLAS tools."""

import logging
from time import perf_counter
from typing import Any

from atlas.tools.base import (
    ToolError,
    ToolExecutionError,
    ToolResult,
)
from atlas.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Execute registered tools and record their outcomes."""

    def __init__(self, registry: ToolRegistry) -> None:
        """Initialize the executor with a tool registry."""
        self._registry = registry

    @property
    def registry(self) -> ToolRegistry:
        """Return the associated tool registry."""
        return self._registry

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute one registered tool."""
        started_at = perf_counter()
        tool = self._registry.get(tool_name)
        definition = tool.definition

        logger.info(
            "Started tool execution. tool=%s risk=%s",
            definition.name,
            definition.risk_level,
        )

        try:
            result = tool.execute(arguments)
        except ToolError:
            logger.exception(
                "Tool execution failed. tool=%s",
                definition.name,
            )
            raise
        except Exception as error:
            logger.exception(
                "Unexpected tool failure. tool=%s",
                definition.name,
            )
            raise ToolExecutionError(f"Tool {definition.name!r} failed unexpectedly.") from error
        finally:
            elapsed_seconds = perf_counter() - started_at

            logger.info(
                "Completed tool execution. tool=%s duration=%.3f",
                definition.name,
                elapsed_seconds,
            )

        logger.info(
            "Tool execution result. tool=%s success=%s",
            definition.name,
            result.success,
        )

        return result
