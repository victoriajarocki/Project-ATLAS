"""Tests for Project ATLAS agent prompt generation."""

import json

import pytest

from atlas.agent.exceptions import AgentConfigurationError
from atlas.agent.prompt import AgentPromptBuilder
from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
)
from atlas.tools.builtin import (
    CalculatorTool,
    CurrentTimeTool,
)
from atlas.tools.registry import ToolRegistry


class ExampleConfirmationTool(Tool):
    """Provide a medium-risk test tool."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the test tool definition."""
        return ToolDefinition(
            name="example_confirmation",
            description="Perform a confirmation-controlled test.",
            parameters={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
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
        arguments: dict[str, object],
    ) -> ToolResult:
        """Return a test result."""
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=str(arguments["message"]),
        )


@pytest.fixture
def registry() -> ToolRegistry:
    """Create a representative tool registry."""
    tool_registry = ToolRegistry()
    tool_registry.register(CalculatorTool())
    tool_registry.register(CurrentTimeTool())
    tool_registry.register(ExampleConfirmationTool())

    return tool_registry


@pytest.fixture
def builder(
    registry: ToolRegistry,
) -> AgentPromptBuilder:
    """Create an agent prompt builder."""
    return AgentPromptBuilder(registry)


def test_decision_prompt_contains_user_request(
    builder: AgentPromptBuilder,
) -> None:
    """The decision prompt should include the user message."""
    prompt = builder.build_decision_prompt("What is 12 multiplied by 8?")

    assert "What is 12 multiplied by 8?" in prompt
    assert "CURRENT USER REQUEST" in prompt


def test_decision_prompt_contains_registered_tools(
    builder: AgentPromptBuilder,
) -> None:
    """Registered tools should appear dynamically."""
    prompt = builder.build_decision_prompt("Help me.")

    assert '"name": "calculator"' in prompt
    assert '"name": "current_time"' in prompt
    assert '"name": "example_confirmation"' in prompt


def test_decision_prompt_contains_parameter_schemas(
    builder: AgentPromptBuilder,
) -> None:
    """Tool schemas should be exposed to the model."""
    prompt = builder.build_decision_prompt("Calculate something.")

    assert '"expression"' in prompt
    assert '"type": "string"' in prompt
    assert '"additionalProperties": false' in prompt


def test_decision_prompt_contains_risk_metadata(
    builder: AgentPromptBuilder,
) -> None:
    """Tool risk information should be included."""
    prompt = builder.build_decision_prompt("Perform an action.")

    assert '"risk_level": "low"' in prompt
    assert '"risk_level": "medium"' in prompt
    assert '"requires_confirmation": true' in prompt


def test_decision_prompt_contains_output_contract(
    builder: AgentPromptBuilder,
) -> None:
    """The model should receive the structured JSON contract."""
    prompt = builder.build_decision_prompt("Hello.")

    assert '{"decision":"respond"' in prompt
    assert '{"decision":"use_tool"' in prompt
    assert "RETURN ONE RAW JSON OBJECT ONLY." in prompt
    assert "Do not include Markdown fences" in prompt


def test_decision_prompt_includes_context_when_present(
    builder: AgentPromptBuilder,
) -> None:
    """Conversation context should be included when supplied."""
    prompt = builder.build_decision_prompt(
        user_message="What is its name?",
        conversation_context=("User: My rocket is named Wraith."),
    )

    assert "CONVERSATION CONTEXT" in prompt
    assert "My rocket is named Wraith." in prompt


def test_decision_prompt_omits_empty_context_heading(
    builder: AgentPromptBuilder,
) -> None:
    """Empty context should not add a context section."""
    prompt = builder.build_decision_prompt(
        user_message="Hello.",
        conversation_context="   ",
    )

    assert "CONVERSATION CONTEXT" not in prompt


def test_decision_prompt_rejects_empty_message(
    builder: AgentPromptBuilder,
) -> None:
    """The prompt builder should reject empty requests."""
    with pytest.raises(
        AgentConfigurationError,
        match="non-empty user message",
    ):
        builder.build_decision_prompt("   ")


def test_tool_catalog_is_valid_json(
    builder: AgentPromptBuilder,
) -> None:
    """The embedded tool catalog should be valid JSON."""
    prompt = builder.build_decision_prompt("Use a tool.")

    catalog_text = prompt.split(
        "AVAILABLE TOOLS\n\n",
        maxsplit=1,
    )[1].split(
        "\n\nCURRENT USER REQUEST",
        maxsplit=1,
    )[0]

    catalog = json.loads(catalog_text)

    assert isinstance(catalog, list)
    assert len(catalog) == 3
    assert {entry["name"] for entry in catalog} == {
        "calculator",
        "current_time",
        "example_confirmation",
    }


def test_tool_result_prompt_contains_original_request(
    builder: AgentPromptBuilder,
) -> None:
    """The final-response prompt should preserve intent."""
    prompt = builder.build_tool_result_prompt(
        user_message="What is 2 + 2?",
        tool_name="calculator",
        tool_output="4",
    )

    assert "ORIGINAL USER REQUEST" in prompt
    assert "What is 2 + 2?" in prompt


def test_tool_result_prompt_contains_tool_result(
    builder: AgentPromptBuilder,
) -> None:
    """The final-response prompt should include tool output."""
    prompt = builder.build_tool_result_prompt(
        user_message="What is 2 + 2?",
        tool_name="calculator",
        tool_output="4",
    )

    assert "TOOL USED" in prompt
    assert "calculator" in prompt
    assert "TOOL RESULT" in prompt
    assert "\n4\n" in prompt


def test_tool_result_prompt_requests_natural_language(
    builder: AgentPromptBuilder,
) -> None:
    """The second prompt should not request JSON."""
    prompt = builder.build_tool_result_prompt(
        user_message="What is 2 + 2?",
        tool_name="calculator",
        tool_output="4",
    )

    assert "Return a concise natural-language response" in prompt
    assert "Do not return JSON" in prompt


def test_tool_result_prompt_includes_context(
    builder: AgentPromptBuilder,
) -> None:
    """Conversation context may accompany a tool result."""
    prompt = builder.build_tool_result_prompt(
        user_message="Read it.",
        tool_name="read_text_file",
        tool_output="Project Wraith",
        conversation_context=("User: The file is Rocket Design/notes.txt."),
    )

    assert "CONVERSATION CONTEXT" in prompt
    assert "Rocket Design/notes.txt" in prompt


@pytest.mark.parametrize(
    ("user_message", "tool_name", "tool_output", "match"),
    [
        (
            "   ",
            "calculator",
            "4",
            "non-empty user message",
        ),
        (
            "What is 2 + 2?",
            "   ",
            "4",
            "requires a tool name",
        ),
        (
            "What is 2 + 2?",
            "calculator",
            "   ",
            "requires tool output",
        ),
    ],
)
def test_tool_result_prompt_rejects_invalid_input(
    builder: AgentPromptBuilder,
    user_message: str,
    tool_name: str,
    tool_output: str,
    match: str,
) -> None:
    """Required tool-result fields should be validated."""
    with pytest.raises(
        AgentConfigurationError,
        match=match,
    ):
        builder.build_tool_result_prompt(
            user_message=user_message,
            tool_name=tool_name,
            tool_output=tool_output,
        )
