"""Data models used by the ATLAS permission system."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from atlas.tools.base import ToolRiskLevel


class PermissionDecision(StrEnum):
    """Describe the result of a permission-policy evaluation."""

    ALLOW = "allow"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass(frozen=True)
class PermissionEvaluation:
    """Represent one permission-policy decision."""

    tool_name: str
    risk_level: ToolRiskLevel
    decision: PermissionDecision
    reason: str


@dataclass(frozen=True)
class PendingToolRequest:
    """Represent a tool request awaiting user confirmation."""

    tool_name: str
    arguments: dict[str, Any]
    risk_level: ToolRiskLevel
