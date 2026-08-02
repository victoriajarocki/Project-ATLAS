"""Tests for the Project ATLAS agent-decision parser."""

import pytest

from atlas.agent.exceptions import AgentParsingError
from atlas.agent.models import AgentDecisionType
from atlas.agent.parser import AgentDecisionParser


@pytest.fixture
def parser() -> AgentDecisionParser:
    """Create an agent-decision parser."""
    return AgentDecisionParser()


def test_parser_accepts_response_decision(
    parser: AgentDecisionParser,
) -> None:
    """A valid response decision should be parsed."""
    decision = parser.parse(
        """
        {
            "decision": "respond",
            "response": "The answer is 42."
        }
        """
    )

    assert decision.decision_type is AgentDecisionType.RESPOND
    assert decision.response == "The answer is 42."
    assert decision.tool_request is None


def test_parser_trims_response_text(
    parser: AgentDecisionParser,
) -> None:
    """Response text should be normalized."""
    decision = parser.parse(
        """
        {
            "decision": "respond",
            "response": "  Hello from ATLAS.  "
        }
        """
    )

    assert decision.response == "Hello from ATLAS."


def test_parser_accepts_tool_decision(
    parser: AgentDecisionParser,
) -> None:
    """A valid tool request should be parsed."""
    decision = parser.parse(
        """
        {
            "decision": "use_tool",
            "tool": {
                "name": "calculator",
                "arguments": {
                    "expression": "2 + 2"
                }
            }
        }
        """
    )

    assert decision.decision_type is AgentDecisionType.USE_TOOL
    assert decision.response is None
    assert decision.tool_request is not None
    assert decision.tool_request.tool_name == "calculator"
    assert decision.tool_request.arguments == {"expression": "2 + 2"}


def test_parser_accepts_empty_tool_arguments(
    parser: AgentDecisionParser,
) -> None:
    """Tools with no parameters should accept an empty object."""
    decision = parser.parse(
        """
        {
            "decision": "use_tool",
            "tool": {
                "name": "current_time",
                "arguments": {}
            }
        }
        """
    )

    assert decision.tool_request is not None
    assert decision.tool_request.tool_name == "current_time"
    assert decision.tool_request.arguments == {}


def test_parser_trims_tool_name(
    parser: AgentDecisionParser,
) -> None:
    """Tool names should be normalized."""
    decision = parser.parse(
        """
        {
            "decision": "use_tool",
            "tool": {
                "name": "  calculator  ",
                "arguments": {
                    "expression": "4 * 4"
                }
            }
        }
        """
    )

    assert decision.tool_request is not None
    assert decision.tool_request.tool_name == "calculator"


def test_parser_rejects_empty_output(
    parser: AgentDecisionParser,
) -> None:
    """Empty model output should fail."""
    with pytest.raises(
        AgentParsingError,
        match="empty agent decision",
    ):
        parser.parse("   ")


def test_parser_rejects_invalid_json(
    parser: AgentDecisionParser,
) -> None:
    """Malformed JSON should fail."""
    with pytest.raises(
        AgentParsingError,
        match="not valid JSON",
    ):
        parser.parse("{not-json}")


def test_parser_rejects_json_array(
    parser: AgentDecisionParser,
) -> None:
    """The top-level value must be an object."""
    with pytest.raises(
        AgentParsingError,
        match="must be a JSON object",
    ):
        parser.parse('["respond"]')


def test_parser_requires_decision_field(
    parser: AgentDecisionParser,
) -> None:
    """A decision field should be required."""
    with pytest.raises(
        AgentParsingError,
        match="requires a string field",
    ):
        parser.parse(
            """
            {
                "response": "Hello."
            }
            """
        )


def test_parser_rejects_unknown_decision(
    parser: AgentDecisionParser,
) -> None:
    """Unsupported decision values should fail."""
    with pytest.raises(
        AgentParsingError,
        match="Unsupported agent decision",
    ):
        parser.parse(
            """
            {
                "decision": "run_shell"
            }
            """
        )


def test_response_decision_requires_response(
    parser: AgentDecisionParser,
) -> None:
    """A response decision should require text."""
    with pytest.raises(
        AgentParsingError,
        match="requires a string field",
    ):
        parser.parse(
            """
            {
                "decision": "respond"
            }
            """
        )


def test_response_decision_rejects_blank_response(
    parser: AgentDecisionParser,
) -> None:
    """Blank response text should fail."""
    with pytest.raises(
        AgentParsingError,
        match="non-empty response text",
    ):
        parser.parse(
            """
            {
                "decision": "respond",
                "response": "   "
            }
            """
        )


def test_response_decision_rejects_unknown_fields(
    parser: AgentDecisionParser,
) -> None:
    """Unknown response fields should fail."""
    with pytest.raises(
        AgentParsingError,
        match="unknown field",
    ):
        parser.parse(
            """
            {
                "decision": "respond",
                "response": "Hello.",
                "tool": {}
            }
            """
        )


def test_tool_decision_requires_tool_object(
    parser: AgentDecisionParser,
) -> None:
    """A tool decision should require a tool object."""
    with pytest.raises(
        AgentParsingError,
        match="requires an object field",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool"
            }
            """
        )


def test_tool_decision_requires_tool_name(
    parser: AgentDecisionParser,
) -> None:
    """A tool request should require a name."""
    with pytest.raises(
        AgentParsingError,
        match="requires a string field",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool",
                "tool": {
                    "arguments": {}
                }
            }
            """
        )


def test_tool_decision_rejects_empty_tool_name(
    parser: AgentDecisionParser,
) -> None:
    """An empty tool name should fail."""
    with pytest.raises(
        AgentParsingError,
        match="cannot be empty",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool",
                "tool": {
                    "name": "   ",
                    "arguments": {}
                }
            }
            """
        )


def test_tool_decision_requires_argument_object(
    parser: AgentDecisionParser,
) -> None:
    """Tool arguments should always be an object."""
    with pytest.raises(
        AgentParsingError,
        match="requires an object field",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool",
                "tool": {
                    "name": "calculator",
                    "arguments": "2 + 2"
                }
            }
            """
        )


def test_tool_decision_rejects_unknown_top_level_fields(
    parser: AgentDecisionParser,
) -> None:
    """Unknown use-tool fields should fail."""
    with pytest.raises(
        AgentParsingError,
        match="unknown field",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool",
                "tool": {
                    "name": "calculator",
                    "arguments": {
                        "expression": "2 + 2"
                    }
                },
                "response": "Calculating."
            }
            """
        )


def test_tool_decision_rejects_unknown_tool_fields(
    parser: AgentDecisionParser,
) -> None:
    """Unknown fields inside the tool object should fail."""
    with pytest.raises(
        AgentParsingError,
        match="tool request contains unknown",
    ):
        parser.parse(
            """
            {
                "decision": "use_tool",
                "tool": {
                    "name": "calculator",
                    "arguments": {
                        "expression": "2 + 2"
                    },
                    "command": "execute"
                }
            }
            """
        )


def test_parser_does_not_accept_markdown_code_fence(
    parser: AgentDecisionParser,
) -> None:
    """The model must return raw JSON rather than Markdown."""
    with pytest.raises(
        AgentParsingError,
        match="not valid JSON",
    ):
        parser.parse(
            """
            ```json
            {
                "decision": "respond",
                "response": "Hello."
            }
            ```
            """
        )
