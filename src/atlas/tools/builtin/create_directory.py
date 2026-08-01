"""Scoped directory-creation tool for Project ATLAS."""

from typing import Any

from atlas.filesystem.exceptions import FileSystemError
from atlas.filesystem.service import FileSystemService
from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
    ToolValidationError,
)


class CreateDirectoryTool(Tool):
    """Create a directory after permission approval."""

    def __init__(
        self,
        filesystem_service: FileSystemService,
    ) -> None:
        """Initialize the directory-creation tool."""
        self._filesystem_service = filesystem_service

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="create_directory",
            description=("Create a directory inside an ATLAS-approved directory."),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "New directory path relative to an allowed ATLAS directory."
                        ),
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.MEDIUM,
            requires_confirmation=True,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Create the requested directory."""
        path_value = arguments.get("path")

        if not isinstance(path_value, str):
            raise ToolValidationError("The create_directory tool requires a string named 'path'.")

        try:
            created_path = self._filesystem_service.create_directory(path_value)
        except FileSystemError as error:
            raise ToolValidationError(str(error)) from error

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=(f"Created directory: {created_path.name}"),
        )
