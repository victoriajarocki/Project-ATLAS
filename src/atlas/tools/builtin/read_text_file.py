"""Scoped text-file reading tool for Project ATLAS."""

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


class ReadTextFileTool(Tool):
    """Read a UTF-8 file from an allowed directory."""

    def __init__(
        self,
        filesystem_service: FileSystemService,
    ) -> None:
        """Initialize the text-file reading tool."""
        self._filesystem_service = filesystem_service

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="read_text_file",
            description=("Read a UTF-8 text file inside an ATLAS-approved directory."),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": ("Text-file path relative to an allowed ATLAS directory."),
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
        """Read and return the requested text file."""
        path_value = arguments.get("path")

        if not isinstance(path_value, str):
            raise ToolValidationError("The read_text_file tool requires a string named 'path'.")

        try:
            result = self._filesystem_service.read_text_file(path_value)
        except FileSystemError as error:
            raise ToolValidationError(str(error)) from error

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=result.content,
        )
