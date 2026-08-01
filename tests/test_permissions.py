"""Tests for the ATLAS permission system."""

from atlas.permissions.models import PermissionDecision
from atlas.permissions.policy import PermissionPolicy
from atlas.permissions.service import PermissionService
from atlas.tools.base import (
    ToolDefinition,
    ToolRiskLevel,
)


def create_definition(
    risk_level: ToolRiskLevel,
    requires_confirmation: bool = False,
) -> ToolDefinition:
    """Create a tool definition for permission tests."""
    return ToolDefinition(
        name="test_tool",
        description="Test permission behavior.",
        parameters={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
    )


def test_low_risk_tool_is_allowed() -> None:
    """Low-risk tools should execute without confirmation."""
    policy = PermissionPolicy()

    evaluation = policy.evaluate(create_definition(ToolRiskLevel.LOW))

    assert evaluation.decision is PermissionDecision.ALLOW


def test_medium_risk_tool_requires_confirmation() -> None:
    """Medium-risk tools should require confirmation."""
    policy = PermissionPolicy()

    evaluation = policy.evaluate(create_definition(ToolRiskLevel.MEDIUM))

    assert evaluation.decision is PermissionDecision.CONFIRM


def test_explicit_confirmation_is_respected() -> None:
    """Confirmation metadata should require approval."""
    policy = PermissionPolicy()

    evaluation = policy.evaluate(
        create_definition(
            ToolRiskLevel.LOW,
            requires_confirmation=True,
        )
    )

    assert evaluation.decision is PermissionDecision.CONFIRM


def test_high_risk_tool_is_denied() -> None:
    """High-risk tools should be denied by default."""
    policy = PermissionPolicy()

    evaluation = policy.evaluate(create_definition(ToolRiskLevel.HIGH))

    assert evaluation.decision is PermissionDecision.DENY


def test_permission_service_returns_policy_decision() -> None:
    """The permission service should expose policy results."""
    service = PermissionService(PermissionPolicy())

    evaluation = service.evaluate(create_definition(ToolRiskLevel.LOW))

    assert evaluation.tool_name == "test_tool"
    assert evaluation.decision is PermissionDecision.ALLOW
