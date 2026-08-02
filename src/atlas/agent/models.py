"""Structured decision models for the Project ATLAS agent."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from atlas.permissions.models import (
    PendingToolRequest,
    PermissionEvaluation,
)


class AgentDecisionType(StrEnum):
    """Describe the next action selected by the model."""

    RESPOND = "respond"
    USE_TOOL = "use_tool"


@dataclass(frozen=True)
class AgentToolRequest:
    """Represent one model-selected tool request."""

    tool_name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class AgentDecision:
    """Represent one structured decision from the model."""

    decision_type: AgentDecisionType
    response: str | None = None
    tool_request: AgentToolRequest | None = None

    def __post_init__(self) -> None:
        """Validate mutually exclusive decision fields."""
        if self.decision_type is AgentDecisionType.RESPOND:
            if self.response is None or not self.response.strip():
                raise ValueError("A respond decision requires response text.")

            if self.tool_request is not None:
                raise ValueError("A respond decision cannot include a tool request.")

        elif self.decision_type is AgentDecisionType.USE_TOOL:
            if self.tool_request is None:
                raise ValueError("A use-tool decision requires a tool request.")

            if self.response is not None:
                raise ValueError("A use-tool decision cannot include response text.")


@dataclass(frozen=True)
class AgentPendingToolRequest:
    """Represent an agent-selected tool awaiting confirmation."""

    request: PendingToolRequest
    evaluation: PermissionEvaluation
    original_user_message: str
    conversation_context: str


@dataclass(frozen=True)
class AgentRunResult:
    """Represent the outcome of one agent-planning cycle."""

    response: str | None = None
    pending_request: AgentPendingToolRequest | None = None

    def __post_init__(self) -> None:
        """Require exactly one agent outcome."""
        has_response = self.response is not None and bool(self.response.strip())
        has_pending_request = self.pending_request is not None

        if has_response == has_pending_request:
            raise ValueError("An agent result requires exactly one of response or pending_request.")
