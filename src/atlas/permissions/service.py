"""Permission coordination for Project ATLAS."""

import logging

from atlas.permissions.models import PermissionEvaluation
from atlas.permissions.policy import PermissionPolicy
from atlas.tools.base import ToolDefinition

logger = logging.getLogger(__name__)


class PermissionService:
    """Evaluate and audit ATLAS permission decisions."""

    def __init__(
        self,
        policy: PermissionPolicy,
    ) -> None:
        """Initialize the permission service."""
        self._policy = policy

    def evaluate(
        self,
        definition: ToolDefinition,
    ) -> PermissionEvaluation:
        """Evaluate and log a tool permission decision."""
        evaluation = self._policy.evaluate(definition)

        logger.info(
            "Permission decision evaluated. tool=%s risk=%s decision=%s requires_confirmation=%s",
            definition.name,
            definition.risk_level,
            evaluation.decision,
            definition.requires_confirmation,
        )

        return evaluation

    def record_confirmation(
        self,
        evaluation: PermissionEvaluation,
        approved: bool,
    ) -> None:
        """Audit the user's confirmation response."""
        logger.info(
            "Tool confirmation resolved. tool=%s risk=%s approved=%s",
            evaluation.tool_name,
            evaluation.risk_level,
            approved,
        )
