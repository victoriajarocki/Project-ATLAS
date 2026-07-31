"""Registration and discovery for ATLAS tools."""

from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolNotFoundError,
)


class ToolRegistry:
    """Store and retrieve tools available to ATLAS."""

    def __init__(self) -> None:
        """Initialize an empty tool registry."""
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool by its unique name."""
        name = tool.definition.name.strip().lower()

        if not name:
            raise ValueError("Tool names cannot be empty.")

        if name in self._tools:
            raise ValueError(f"A tool named {name!r} is already registered.")

        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        """Return a registered tool by name."""
        normalized_name = name.strip().lower()

        try:
            return self._tools[normalized_name]
        except KeyError as error:
            raise ToolNotFoundError(f"Tool {normalized_name!r} is not registered.") from error

    def list_definitions(self) -> list[ToolDefinition]:
        """Return definitions for all registered tools."""
        return sorted(
            (tool.definition for tool in self._tools.values()),
            key=lambda definition: definition.name,
        )

    def contains(self, name: str) -> bool:
        """Report whether a tool is registered."""
        return name.strip().lower() in self._tools
