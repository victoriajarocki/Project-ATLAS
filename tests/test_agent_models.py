"""Tests for Project ATLAS agent decision models."""

import pytest

from atlas.agent.models import (
    AgentDecision,
    AgentDecisionType,
    AgentToolRequest,
)


def test_respond_decision_accepts_response_text() -> None:
    """A response decision should contain natural-language text."""
    decision = AgentDecision(
        decision_type=AgentDecisionType.RESPOND,
        response="The answer is 42.",
    )

    assert decision.response == "The answer is 42."
    assert decision.tool_request is None


def test_respond_decision_rejects_empty_response() -> None:
    """A response decision should reject blank text."""
    with pytest.raises(
        ValueError,
        match="requires response text",
    ):
        AgentDecision(
            decision_type=AgentDecisionType.RESPOND,
            response="   ",
        )


def test_respond_decision_rejects_tool_request() -> None:
    """A response decision cannot request a tool."""
    request = AgentToolRequest(
        tool_name="calculator",
        arguments={"expression": "2 + 2"},
    )

    with pytest.raises(
        ValueError,
        match="cannot include a tool request",
    ):
        AgentDecision(
            decision_type=AgentDecisionType.RESPOND,
            response="Use the calculator.",
            tool_request=request,
        )


def test_tool_decision_accepts_tool_request() -> None:
    """A tool decision should contain one structured request."""
    request = AgentToolRequest(
        tool_name="calculator",
        arguments={"expression": "2 + 2"},
    )

    decision = AgentDecision(
        decision_type=AgentDecisionType.USE_TOOL,
        tool_request=request,
    )

    assert decision.response is None
    assert decision.tool_request == request


def test_tool_decision_rejects_missing_request() -> None:
    """A use-tool decision should require a request."""
    with pytest.raises(
        ValueError,
        match="requires a tool request",
    ):
        AgentDecision(
            decision_type=AgentDecisionType.USE_TOOL,
        )


def test_tool_decision_rejects_response_text() -> None:
    """A use-tool decision cannot also contain a response."""
    request = AgentToolRequest(
        tool_name="calculator",
        arguments={"expression": "2 + 2"},
    )

    with pytest.raises(
        ValueError,
        match="cannot include response text",
    ):
        AgentDecision(
            decision_type=AgentDecisionType.USE_TOOL,
            response="Calculating.",
            tool_request=request,
        )
