"""Scoped text-file writing tool for Project ATLAS."""

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


class WriteTextFileTool(Tool):
    """Write UTF-8 text after permission approval."""

    def __init__(
        self,
        filesystem_service: FileSystemService,
    ) -> None:
        """Initialize the text-file writing tool."""
        self._filesystem_service = filesystem_service

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="write_text_file",
            description=("Write UTF-8 text inside an ATLAS-approved directory."),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": ("File path relative to an allowed ATLAS directory."),
                    },
                    "content": {
                        "type": "string",
                        "description": ("UTF-8 text to write."),
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": ("Whether an existing file may be replaced."),
                        "default": False,
                    },
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.MEDIUM,
            requires_confirmation=True,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Write the requested text file."""
        path_value = arguments.get("path")
        content_value = arguments.get("content")
        overwrite_value = arguments.get(
            "overwrite",
            False,
        )

        if not isinstance(path_value, str):
            raise ToolValidationError("The write_text_file tool requires a string named 'path'.")

        if not isinstance(content_value, str):
            raise ToolValidationError("The write_text_file tool requires a string named 'content'.")

        if not isinstance(overwrite_value, bool):
            raise ToolValidationError("The overwrite argument must be true or false.")

        try:
            result = self._filesystem_service.write_text_file(
                requested_path=path_value,
                content=content_value,
                overwrite=overwrite_value,
            )
        except FileSystemError as error:
            raise ToolValidationError(str(error)) from error

        action = "Created" if result.created else "Overwrote"

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=(f"{action} file: {result.path.name} ({result.character_count} characters)"),
        )
