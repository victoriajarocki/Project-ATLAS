"""Tests for the Project ATLAS agent service."""

from collections.abc import Iterator

import pytest

from atlas.agent.exceptions import (
    AgentConfigurationError,
    AgentDecisionError,
)
from atlas.agent.parser import AgentDecisionParser
from atlas.agent.prompt import AgentPromptBuilder
from atlas.agent.service import AgentService
from atlas.models.base import ModelProvider
from atlas.permissions.policy import PermissionPolicy
from atlas.permissions.service import PermissionService
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
from atlas.tools.executor import ToolExecutor
from atlas.tools.registry import ToolRegistry


class ScriptedModelProvider(ModelProvider):
    """Return predefined model responses in sequence."""

    def __init__(
        self,
        responses: list[str],
    ) -> None:
        """Initialize the scripted provider."""
        self._responses: Iterator[str] = iter(responses)
        self.inputs: list[str] = []

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Scripted"

    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Record input and return the next response."""
        self.inputs.append(user_message)

        try:
            return next(self._responses)
        except StopIteration as error:
            raise RuntimeError("No scripted model response remains.") from error


class MediumRiskTool(Tool):
    """Provide a confirmation-controlled test tool."""

    def __init__(self) -> None:
        """Initialize execution tracking."""
        self.execution_count = 0

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="medium_action",
            description="Perform a medium-risk test action.",
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
        """Execute the test action."""
        self.execution_count += 1

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=str(arguments["message"]),
        )


class HighRiskTool(Tool):
    """Provide a denied high-risk test tool."""

    def __init__(self) -> None:
        """Initialize execution tracking."""
        self.execution_count = 0

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="high_action",
            description="Perform a high-risk test action.",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.HIGH,
            requires_confirmation=True,
        )

    def execute(
        self,
        arguments: dict[str, object],
    ) -> ToolResult:
        """Record unexpected execution."""
        self.execution_count += 1

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output="Executed.",
        )


def create_service(
    responses: list[str],
) -> tuple[
    AgentService,
    ScriptedModelProvider,
    MediumRiskTool,
    HighRiskTool,
]:
    """Create an agent service with representative tools."""
    provider = ScriptedModelProvider(responses)

    medium_tool = MediumRiskTool()
    high_tool = HighRiskTool()

    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(CurrentTimeTool())
    registry.register(medium_tool)
    registry.register(high_tool)

    executor = ToolExecutor(registry)

    permission_service = PermissionService(PermissionPolicy())

    service = AgentService(
        model_provider=provider,
        prompt_builder=AgentPromptBuilder(registry),
        decision_parser=AgentDecisionParser(),
        tool_executor=executor,
        permission_service=permission_service,
    )

    return (
        service,
        provider,
        medium_tool,
        high_tool,
    )


def test_agent_returns_direct_model_response() -> None:
    """The model may answer without selecting a tool."""
    service, provider, _, _ = create_service(
        [('{"decision":"respond","response":"Hello from ATLAS."}')]
    )

    result = service.process_request("Hello.")

    assert result.response == "Hello from ATLAS."
    assert result.pending_request is None
    assert len(provider.inputs) == 1
    assert "CURRENT USER REQUEST" in provider.inputs[0]


def test_agent_executes_low_risk_tool() -> None:
    """A low-risk tool should execute automatically."""
    service, provider, _, _ = create_service(
        [
            (
                '{"decision":"use_tool","tool":'
                '{"name":"calculator","arguments":'
                '{"expression":"12 * 4"}}}'
            )
        ]
    )

    result = service.process_request("What is 12 multiplied by 4?")

    assert result.response == "48"
    assert result.pending_request is None
    assert len(provider.inputs) == 1
    assert '"name": "calculator"' in provider.inputs[0]


def test_agent_passes_conversation_context() -> None:
    """Conversation context should reach the decision prompt."""
    service, provider, _, _ = create_service(
        [
            (
                '{"decision":"use_tool","tool":'
                '{"name":"calculator","arguments":'
                '{"expression":"2 + 2"}}}'
            )
        ]
    )

    result = service.process_request(
        user_message="Calculate it.",
        conversation_context=("User: The expression is 2 + 2."),
    )

    assert result.response == "4"
    assert len(provider.inputs) == 1
    assert "The expression is 2 + 2." in provider.inputs[0]


def test_agent_rejects_empty_user_message() -> None:
    """Empty agent requests should be rejected."""
    service, _, _, _ = create_service([])

    with pytest.raises(
        AgentConfigurationError,
        match="non-empty user message",
    ):
        service.process_request("   ")


def test_agent_rejects_unknown_model_selected_tool() -> None:
    """Invented tools should fail safely."""
    service, _, _, _ = create_service(
        [('{"decision":"use_tool","tool":{"name":"shell","arguments":{}}}')]
    )

    with pytest.raises(
        AgentDecisionError,
        match="unavailable tool",
    ):
        service.process_request("Run a shell command.")


def test_agent_rejects_invalid_tool_arguments() -> None:
    """Invalid model-generated arguments should fail."""
    service, _, _, _ = create_service(
        [('{"decision":"use_tool","tool":{"name":"calculator","arguments":{}}}')]
    )

    with pytest.raises(
        AgentDecisionError,
        match="invalid arguments",
    ):
        service.process_request("Calculate something.")


def test_medium_risk_tool_requires_confirmation() -> None:
    """Medium-risk tools should become pending."""
    service, provider, medium_tool, _ = create_service(
        [
            (
                '{"decision":"use_tool","tool":'
                '{"name":"medium_action","arguments":'
                '{"message":"Approved action"}}}'
            )
        ]
    )

    result = service.process_request("Perform the medium action.")

    assert result.response is None
    assert result.pending_request is not None
    assert result.pending_request.request.tool_name == "medium_action"
    assert medium_tool.execution_count == 0
    assert len(provider.inputs) == 1


def test_confirmed_medium_risk_tool_executes() -> None:
    """Approved pending requests should execute once."""
    service, provider, medium_tool, _ = create_service(
        [
            (
                '{"decision":"use_tool","tool":'
                '{"name":"medium_action","arguments":'
                '{"message":"Approved action"}}}'
            )
        ]
    )

    result = service.process_request("Perform the medium action.")

    assert result.pending_request is not None

    response = service.complete_confirmed_request(result.pending_request)

    assert response == "Approved action"
    assert medium_tool.execution_count == 1
    assert len(provider.inputs) == 1


def test_denied_medium_risk_tool_does_not_execute() -> None:
    """Denied pending requests should remain unexecuted."""
    service, provider, medium_tool, _ = create_service(
        [
            (
                '{"decision":"use_tool","tool":'
                '{"name":"medium_action","arguments":'
                '{"message":"Do not run"}}}'
            )
        ]
    )

    result = service.process_request("Perform the medium action.")

    assert result.pending_request is not None

    response = service.deny_confirmed_request(result.pending_request)

    assert response == ("Tool medium_action execution was denied.")
    assert medium_tool.execution_count == 0
    assert len(provider.inputs) == 1


def test_high_risk_tool_is_denied() -> None:
    """High-risk tools should never execute."""
    service, provider, _, high_tool = create_service(
        [('{"decision":"use_tool","tool":{"name":"high_action","arguments":{}}}')]
    )

    result = service.process_request("Perform the high-risk action.")

    assert result.pending_request is None
    assert result.response is not None
    assert "was denied" in result.response
    assert high_tool.execution_count == 0
    assert len(provider.inputs) == 1
