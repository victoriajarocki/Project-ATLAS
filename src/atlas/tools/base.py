"""Shared interfaces and data models for ATLAS tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ToolRiskLevel(StrEnum):
    """Describe the potential impact of executing a tool."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ToolDefinition:
    """Describe a registered ATLAS tool."""

    name: str
    description: str
    parameters: dict[str, Any]
    risk_level: ToolRiskLevel
    requires_confirmation: bool


@dataclass(frozen=True)
class ToolResult:
    """Represent the result of a tool execution."""

    tool_name: str
    success: bool
    output: str
    error: str | None = None


class ToolError(RuntimeError):
    """Base exception raised by the ATLAS tool system."""


class ToolValidationError(ToolError):
    """Raised when tool arguments are invalid."""


class ToolExecutionError(ToolError):
    """Raised when a tool fails during execution."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class Tool(ABC):
    """Abstract interface implemented by every ATLAS tool."""

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""

    @abstractmethod
    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Execute the tool using validated arguments."""
