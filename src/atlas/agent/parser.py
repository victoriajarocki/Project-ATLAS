"""Parse structured model output into ATLAS agent decisions."""

import json
from typing import Any

from atlas.agent.exceptions import AgentParsingError
from atlas.agent.models import (
    AgentDecision,
    AgentDecisionType,
    AgentToolRequest,
)


class AgentDecisionParser:
    """Convert structured model output into agent decisions."""

    def parse(
        self,
        model_output: str,
    ) -> AgentDecision:
        """Parse one structured agent decision."""
        cleaned_output = model_output.strip()

        if not cleaned_output:
            raise AgentParsingError("The model returned an empty agent decision.")

        try:
            parsed_output: Any = json.loads(cleaned_output)
        except json.JSONDecodeError as error:
            raise AgentParsingError("The model response was not valid JSON.") from error

        if not isinstance(parsed_output, dict):
            raise AgentParsingError("The agent decision must be a JSON object.")

        decision_value = parsed_output.get("decision")

        if not isinstance(decision_value, str):
            raise AgentParsingError("The agent decision requires a string field named 'decision'.")

        try:
            decision_type = AgentDecisionType(decision_value)
        except ValueError as error:
            raise AgentParsingError(f"Unsupported agent decision: {decision_value!r}.") from error

        if decision_type is AgentDecisionType.RESPOND:
            return self._parse_response_decision(parsed_output)

        if decision_type is AgentDecisionType.USE_TOOL:
            return self._parse_tool_decision(parsed_output)

        raise AgentParsingError("The model selected an unsupported agent decision.")

    @staticmethod
    def _parse_response_decision(
        parsed_output: dict[str, Any],
    ) -> AgentDecision:
        """Parse a natural-language response decision."""
        allowed_keys = {
            "decision",
            "response",
        }

        unknown_keys = sorted(set(parsed_output) - allowed_keys)

        if unknown_keys:
            formatted_keys = ", ".join(unknown_keys)

            raise AgentParsingError(
                f"A respond decision contains unknown field(s): {formatted_keys}."
            )

        response_value = parsed_output.get("response")

        if not isinstance(response_value, str):
            raise AgentParsingError("A respond decision requires a string field named 'response'.")

        cleaned_response = response_value.strip()

        if not cleaned_response:
            raise AgentParsingError("A respond decision requires non-empty response text.")

        return AgentDecision(
            decision_type=AgentDecisionType.RESPOND,
            response=cleaned_response,
        )

    @staticmethod
    def _parse_tool_decision(
        parsed_output: dict[str, Any],
    ) -> AgentDecision:
        """Parse a structured tool-use decision."""
        allowed_keys = {
            "decision",
            "tool",
        }

        unknown_keys = sorted(set(parsed_output) - allowed_keys)

        if unknown_keys:
            formatted_keys = ", ".join(unknown_keys)

            raise AgentParsingError(
                f"A use-tool decision contains unknown field(s): {formatted_keys}."
            )

        tool_value = parsed_output.get("tool")

        if not isinstance(tool_value, dict):
            raise AgentParsingError("A use-tool decision requires an object field named 'tool'.")

        allowed_tool_keys = {
            "name",
            "arguments",
        }

        unknown_tool_keys = sorted(set(tool_value) - allowed_tool_keys)

        if unknown_tool_keys:
            formatted_keys = ", ".join(unknown_tool_keys)

            raise AgentParsingError(
                f"The tool request contains unknown field(s): {formatted_keys}."
            )

        tool_name_value = tool_value.get("name")

        if not isinstance(tool_name_value, str):
            raise AgentParsingError("The tool request requires a string field named 'name'.")

        cleaned_tool_name = tool_name_value.strip()

        if not cleaned_tool_name:
            raise AgentParsingError("The tool name cannot be empty.")

        arguments_value = tool_value.get("arguments")

        if not isinstance(arguments_value, dict):
            raise AgentParsingError("The tool request requires an object field named 'arguments'.")

        tool_request = AgentToolRequest(
            tool_name=cleaned_tool_name,
            arguments=dict(arguments_value),
        )

        return AgentDecision(
            decision_type=AgentDecisionType.USE_TOOL,
            tool_request=tool_request,
        )
