"""Build structured prompts for the Project ATLAS agent."""

import json
from typing import Any

from atlas.agent.exceptions import AgentConfigurationError
from atlas.tools.base import ToolDefinition
from atlas.tools.registry import ToolRegistry


class AgentPromptBuilder:
    """Build agent instructions from registered ATLAS tools."""

    def __init__(
        self,
        tool_registry: ToolRegistry,
    ) -> None:
        """Initialize the prompt builder."""
        self._tool_registry = tool_registry

    def build_decision_prompt(
        self,
        user_message: str,
        conversation_context: str = "",
    ) -> str:
        """Build the prompt used for the first agent decision."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            raise AgentConfigurationError("The agent requires a non-empty user message.")

        tool_catalog = self._build_tool_catalog()

        sections = [
            self._build_system_instructions(),
            "AVAILABLE TOOLS",
            tool_catalog,
        ]

        cleaned_context = conversation_context.strip()

        if cleaned_context:
            sections.extend(
                [
                    "CONVERSATION CONTEXT",
                    cleaned_context,
                ]
            )

        sections.extend(
            [
                "CURRENT USER REQUEST",
                cleaned_message,
                "RETURN ONE RAW JSON OBJECT ONLY.",
            ]
        )

        return "\n\n".join(sections)

    def build_tool_result_prompt(
        self,
        user_message: str,
        tool_name: str,
        tool_output: str,
        conversation_context: str = "",
    ) -> str:
        """Build a prompt asking the model for a final response."""
        cleaned_message = user_message.strip()
        cleaned_tool_name = tool_name.strip()
        cleaned_tool_output = tool_output.strip()

        if not cleaned_message:
            raise AgentConfigurationError("The agent requires a non-empty user message.")

        if not cleaned_tool_name:
            raise AgentConfigurationError("A tool-result prompt requires a tool name.")

        if not cleaned_tool_output:
            raise AgentConfigurationError("A tool-result prompt requires tool output.")

        sections = [
            ("You are ATLAS, a professional personal AI and engineering assistant."),
            (
                "A tool has completed successfully. Use its "
                "result to answer the user's original request."
            ),
            (
                "Do not claim that you performed any action "
                "other than the one represented by the tool result."
            ),
            ("Return a concise natural-language response. Do not return JSON."),
        ]

        cleaned_context = conversation_context.strip()

        if cleaned_context:
            sections.extend(
                [
                    "CONVERSATION CONTEXT",
                    cleaned_context,
                ]
            )

        sections.extend(
            [
                "ORIGINAL USER REQUEST",
                cleaned_message,
                "TOOL USED",
                cleaned_tool_name,
                "TOOL RESULT",
                cleaned_tool_output,
                "FINAL RESPONSE",
            ]
        )

        return "\n\n".join(sections)

    def _build_tool_catalog(self) -> str:
        """Build a JSON catalog from registered tool definitions."""
        definitions = self._tool_registry.list_definitions()

        catalog = [self._serialize_definition(definition) for definition in definitions]

        return json.dumps(
            catalog,
            indent=2,
            sort_keys=True,
        )

    @staticmethod
    def _serialize_definition(
        definition: ToolDefinition,
    ) -> dict[str, Any]:
        """Convert a tool definition into prompt-safe data."""
        return {
            "name": definition.name,
            "description": definition.description,
            "parameters": definition.parameters,
            "risk_level": definition.risk_level.value,
            "requires_confirmation": (definition.requires_confirmation),
        }

    @staticmethod
    def _build_system_instructions() -> str:
        """Return the structured agent decision instructions."""
        return "\n".join(
            [
                ("You are ATLAS, a professional personal AI and engineering assistant."),
                ("Decide whether to answer directly or request exactly one registered tool."),
                (
                    "Use a tool whenever the user requests an action "
                    "that a registered tool can perform."
                ),
                (
                    "Use a tool when it materially improves accuracy "
                    "or retrieves current local information."
                ),
                (
                    "Never invent tool names, parameters, files, "
                    "results, permissions, or capabilities."
                ),
                (
                    "Never request shell commands, arbitrary code "
                    "execution, or an unregistered tool."
                ),
                ("Tool arguments must exactly match the supplied parameter schema."),
                (
                    "Never claim that an action was completed unless "
                    "a registered tool was actually selected and executed."
                ),
                (
                    "Do not return a respond decision for a requested "
                    "action that requires a registered tool."
                ),
                (
                    "Requests to create, write, modify, or save files "
                    "must use the appropriate registered filesystem tool."
                ),
                (
                    "When the user asks to create or write a text file, "
                    "select write_text_file with the requested path and content."
                ),
                (
                    "When the user asks to create a directory or folder, "
                    "select create_directory with the requested path."
                ),
                (
                    "When the user asks for the current local time or date, "
                    "select current_time instead of answering from memory."
                ),
                (
                    "When the user refers to 'my workspace' or "
                    "'the workspace' without naming a path, use "
                    "list_directory with path '.'."
                ),
                (
                    "Do not ask the user for a filesystem path when "
                    "the request clearly refers to the configured "
                    "ATLAS workspace."
                ),
                (
                    "Use read_text_file when the user asks to read "
                    "a named text file inside the workspace."
                ),
                (
                    "Use file_info when the user asks for metadata, "
                    "size, type, or modification details about a file."
                ),
                ("Use calculator for arithmetic rather than solving the expression directly."),
                ("Do not include Markdown fences, explanations, or text outside the JSON object."),
                "",
                "For a direct response, return:",
                ('{"decision":"respond","response":"Your response here."}'),
                "",
                "For a tool request, return:",
                ('{"decision":"use_tool","tool":{"name":"registered_tool_name","arguments":{}}}'),
            ]
        )
