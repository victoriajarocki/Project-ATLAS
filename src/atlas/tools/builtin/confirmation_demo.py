"""Safe confirmation demonstration tool for Project ATLAS."""

from typing import Any

from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
    ToolValidationError,
)


class ConfirmationDemoTool(Tool):
    """Demonstrate confirmation-controlled tool execution."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="confirmation_demo",
            description=(
                "Return a supplied message after explicit user "
                "confirmation. This tool exists to test permissions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": ("Message returned after confirmation."),
                    }
                },
                "required": ["message"],
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.MEDIUM,
            requires_confirmation=True,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Return the confirmed demonstration message."""
        message_value = arguments.get("message")

        if not isinstance(message_value, str):
            raise ToolValidationError(
                "The confirmation_demo tool requires a string named 'message'."
            )

        message = message_value.strip()

        if not message:
            raise ToolValidationError("The demonstration message cannot be empty.")

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=message,
        )
