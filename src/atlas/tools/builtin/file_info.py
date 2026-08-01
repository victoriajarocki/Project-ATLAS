"""File metadata tool for Project ATLAS."""

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


class FileInfoTool(Tool):
    """Return metadata for an allowed file or directory."""

    def __init__(
        self,
        filesystem_service: FileSystemService,
    ) -> None:
        """Initialize the file-information tool."""
        self._filesystem_service = filesystem_service

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="file_info",
            description=(
                "Inspect metadata for a file or directory inside an ATLAS-approved directory."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": (
                            "File or directory path relative to an allowed ATLAS directory."
                        ),
                    }
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Return metadata for the requested path."""
        path_value = arguments.get("path")

        if not isinstance(path_value, str):
            raise ToolValidationError("The file_info tool requires a string named 'path'.")

        try:
            entry = self._filesystem_service.get_info(path_value)
        except FileSystemError as error:
            raise ToolValidationError(str(error)) from error

        size_text = "not applicable" if entry.size_bytes is None else f"{entry.size_bytes} bytes"

        output = "\n".join(
            [
                f"Name: {entry.name}",
                f"Type: {entry.entry_type}",
                f"Size: {size_text}",
                (f"Modified: {entry.modified_at.isoformat(timespec='seconds')}"),
            ]
        )

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=output,
        )
