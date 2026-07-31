"""Local system-time tool for Project ATLAS."""

from datetime import datetime
from typing import Any

from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
    ToolValidationError,
)


class CurrentTimeTool(Tool):
    """Return the computer's current local date and time."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the current-time tool definition."""
        return ToolDefinition(
            name="current_time",
            description=("Return the current local date and time from the computer running ATLAS."),
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Return the current local date and time."""
        if arguments:
            raise ToolValidationError("The current_time tool does not accept arguments.")

        current_time = datetime.now().astimezone()

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=current_time.isoformat(timespec="seconds"),
        )
