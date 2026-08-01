"""Directory-listing tool for Project ATLAS."""

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


class ListDirectoryTool(Tool):
    """List files and directories inside an allowed path."""

    def __init__(
        self,
        filesystem_service: FileSystemService,
    ) -> None:
        """Initialize the directory-listing tool."""
        self._filesystem_service = filesystem_service

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="list_directory",
            description=("List files and directories inside an ATLAS-approved directory."),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": ("Directory path relative to an allowed ATLAS directory."),
                    }
                },
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """List entries in the requested directory."""
        path_value = arguments.get("path", ".")

        if not isinstance(path_value, str):
            raise ToolValidationError("The path must be a string.")

        try:
            entries = self._filesystem_service.list_directory(path_value)
        except FileSystemError as error:
            raise ToolValidationError(str(error)) from error

        if not entries:
            output = "The directory is empty."
        else:
            lines: list[str] = []

            for entry in entries:
                if entry.size_bytes is None:
                    size_text = "-"
                else:
                    size_text = str(entry.size_bytes)

                lines.append(f"{entry.entry_type}: {entry.name} (size: {size_text} bytes)")

            output = "\n".join(lines)

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=output,
        )
