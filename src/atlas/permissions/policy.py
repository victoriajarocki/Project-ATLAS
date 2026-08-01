"""Permission-policy evaluation for Project ATLAS."""

from atlas.permissions.models import (
    PermissionDecision,
    PermissionEvaluation,
)
from atlas.tools.base import ToolDefinition, ToolRiskLevel


class PermissionPolicy:
    """Evaluate whether a requested tool may execute."""

    def evaluate(
        self,
        definition: ToolDefinition,
    ) -> PermissionEvaluation:
        """Evaluate the supplied tool definition."""
        if definition.risk_level is ToolRiskLevel.HIGH:
            return PermissionEvaluation(
                tool_name=definition.name,
                risk_level=definition.risk_level,
                decision=PermissionDecision.DENY,
                reason=("High-risk tools are denied by the default ATLAS permission policy."),
            )

        if definition.risk_level is ToolRiskLevel.MEDIUM or definition.requires_confirmation:
            return PermissionEvaluation(
                tool_name=definition.name,
                risk_level=definition.risk_level,
                decision=PermissionDecision.CONFIRM,
                reason=("This tool requires explicit user confirmation before execution."),
            )

        return PermissionEvaluation(
            tool_name=definition.name,
            risk_level=definition.risk_level,
            decision=PermissionDecision.ALLOW,
            reason=("This low-risk tool may execute without confirmation."),
        )
