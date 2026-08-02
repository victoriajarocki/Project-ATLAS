"""Agent orchestration service for Project ATLAS."""

import logging
import re
from typing import Any

from atlas.agent.exceptions import (
    AgentConfigurationError,
    AgentDecisionError,
    AgentError,
)
from atlas.agent.models import (
    AgentDecisionType,
    AgentPendingToolRequest,
    AgentRunResult,
)
from atlas.agent.parser import AgentDecisionParser
from atlas.agent.prompt import AgentPromptBuilder
from atlas.models.base import ModelError, ModelProvider
from atlas.permissions.models import (
    PendingToolRequest,
    PermissionDecision,
)
from atlas.permissions.service import PermissionService
from atlas.tools.base import (
    ToolError,
    ToolResult,
    ToolValidationError,
)
from atlas.tools.executor import ToolExecutor

logger = logging.getLogger(__name__)


AGENT_DECISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "decision": {
            "type": "string",
            "enum": [
                "respond",
                "use_tool",
            ],
        },
        "response": {
            "type": [
                "string",
                "null",
            ],
        },
        "tool": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                        },
                        "arguments": {
                            "type": "object",
                        },
                    },
                    "required": [
                        "name",
                        "arguments",
                    ],
                    "additionalProperties": False,
                },
                {
                    "type": "null",
                },
            ],
        },
    },
    "required": [
        "decision",
    ],
    "additionalProperties": False,
}


_FILE_CREATION_PATTERN = re.compile(
    r"""
    ^\s*
    create\s+(?:a\s+)?
    file\s+(?:called|named)\s+
    (?P<path>.+?)
    \s+that\s+(?:says|contains)\s+
    (?P<content>.+?)
    [.!]?\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


_DIRECTORY_CREATION_PATTERN = re.compile(
    r"""
    ^\s*
    create\s+(?:a\s+)?
    (?:folder|directory)\s+
    (?:called|named)\s+
    (?P<path>.+?)
    [.!]?\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)


class AgentService:
    """Coordinate model decisions, permissions, and tools."""

    def __init__(
        self,
        model_provider: ModelProvider,
        prompt_builder: AgentPromptBuilder,
        decision_parser: AgentDecisionParser,
        tool_executor: ToolExecutor,
        permission_service: PermissionService,
    ) -> None:
        """Initialize the agent service."""
        self._model_provider = model_provider
        self._prompt_builder = prompt_builder
        self._decision_parser = decision_parser
        self._tool_executor = tool_executor
        self._permission_service = permission_service

    def process_request(
        self,
        user_message: str,
        conversation_context: str = "",
    ) -> AgentRunResult:
        """Process one natural-language request."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            raise AgentConfigurationError("The agent requires a non-empty user message.")

        required_action = self._route_required_action(
            user_message=cleaned_message,
            conversation_context=conversation_context,
        )

        if required_action is not None:
            return required_action

        decision_prompt = self._prompt_builder.build_decision_prompt(
            user_message=cleaned_message,
            conversation_context=conversation_context,
        )

        logger.info(
            "Requesting structured agent decision. message_length=%d",
            len(cleaned_message),
        )

        try:
            model_output = self._model_provider.generate_structured_response(
                user_message=decision_prompt,
                schema=AGENT_DECISION_SCHEMA,
            )
        except ModelError as error:
            raise AgentError("The model failed while creating an agent decision.") from error

        decision = self._decision_parser.parse(model_output)

        if decision.decision_type is AgentDecisionType.RESPOND:
            if decision.response is None:
                raise AgentDecisionError(
                    "The agent response decision did not contain response text."
                )

            logger.info("Agent selected a direct response.")

            return AgentRunResult(response=decision.response)

        if decision.tool_request is None:
            raise AgentDecisionError("The agent selected tool use without a tool request.")

        return self._process_tool_request(
            user_message=cleaned_message,
            conversation_context=conversation_context,
            tool_name=decision.tool_request.tool_name,
            arguments=decision.tool_request.arguments,
        )

    def complete_confirmed_request(
        self,
        pending_request: AgentPendingToolRequest,
    ) -> str:
        """Execute an approved request and return the result."""
        self._permission_service.record_confirmation(
            evaluation=pending_request.evaluation,
            approved=True,
        )

        result = self._execute_tool(
            tool_name=pending_request.request.tool_name,
            arguments=pending_request.request.arguments,
        )

        return self._generate_final_response(
            user_message=pending_request.original_user_message,
            conversation_context=(pending_request.conversation_context),
            tool_name=result.tool_name,
            tool_output=result.output,
        )

    def deny_confirmed_request(
        self,
        pending_request: AgentPendingToolRequest,
    ) -> str:
        """Record denial of a pending agent request."""
        self._permission_service.record_confirmation(
            evaluation=pending_request.evaluation,
            approved=False,
        )

        logger.info(
            "Agent-selected tool denied by user. tool=%s risk=%s",
            pending_request.request.tool_name,
            pending_request.request.risk_level,
        )

        return f"Tool {pending_request.request.tool_name} execution was denied."

    def _route_required_action(
        self,
        user_message: str,
        conversation_context: str,
    ) -> AgentRunResult | None:
        """Route obvious state-changing actions deterministically."""
        file_match = _FILE_CREATION_PATTERN.fullmatch(user_message)

        if file_match is not None:
            path = self._clean_action_value(file_match.group("path"))
            content = self._clean_action_value(file_match.group("content"))

            logger.info("Deterministically routed file-creation request.")

            return self._process_tool_request(
                user_message=user_message,
                conversation_context=conversation_context,
                tool_name="write_text_file",
                arguments={
                    "path": path,
                    "content": content,
                },
            )

        directory_match = _DIRECTORY_CREATION_PATTERN.fullmatch(user_message)

        if directory_match is not None:
            path = self._clean_action_value(directory_match.group("path"))

            logger.info("Deterministically routed directory-creation request.")

            return self._process_tool_request(
                user_message=user_message,
                conversation_context=conversation_context,
                tool_name="create_directory",
                arguments={
                    "path": path,
                },
            )

        return None

    @staticmethod
    def _clean_action_value(
        value: str,
    ) -> str:
        """Normalize a path or content value from a request."""
        cleaned_value = value.strip()

        if (
            len(cleaned_value) >= 2
            and cleaned_value[0] == cleaned_value[-1]
            and cleaned_value[0] in {"'", '"', "`"}
        ):
            cleaned_value = cleaned_value[1:-1].strip()

        return cleaned_value

    def _process_tool_request(
        self,
        user_message: str,
        conversation_context: str,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> AgentRunResult:
        """Validate and authorize a model-selected tool."""
        try:
            tool = self._tool_executor.registry.get(tool_name)
        except ToolError as error:
            raise AgentDecisionError(
                f"The model selected an unavailable tool: {tool_name!r}."
            ) from error

        try:
            self._tool_executor.validate_arguments(
                tool_name=tool.definition.name,
                arguments=arguments,
            )
        except ToolValidationError as error:
            raise AgentDecisionError(
                f"The model generated invalid arguments for tool {tool.definition.name!r}: {error}"
            ) from error

        evaluation = self._permission_service.evaluate(tool.definition)

        if evaluation.decision is PermissionDecision.DENY:
            logger.warning(
                "Agent-selected tool denied by policy. tool=%s risk=%s",
                evaluation.tool_name,
                evaluation.risk_level,
            )

            return AgentRunResult(
                response=(f"Tool {evaluation.tool_name} was denied. Reason: {evaluation.reason}")
            )

        if evaluation.decision is PermissionDecision.CONFIRM:
            logger.info(
                "Agent-selected tool requires confirmation. tool=%s risk=%s",
                evaluation.tool_name,
                evaluation.risk_level,
            )

            pending_request = AgentPendingToolRequest(
                request=PendingToolRequest(
                    tool_name=tool.definition.name,
                    arguments=dict(arguments),
                    risk_level=tool.definition.risk_level,
                ),
                evaluation=evaluation,
                original_user_message=user_message,
                conversation_context=conversation_context,
            )

            return AgentRunResult(pending_request=pending_request)

        result = self._execute_tool(
            tool_name=tool.definition.name,
            arguments=arguments,
        )

        response = self._generate_final_response(
            user_message=user_message,
            conversation_context=conversation_context,
            tool_name=result.tool_name,
            tool_output=result.output,
        )

        return AgentRunResult(response=response)

    def _execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute one authorized tool."""
        try:
            return self._tool_executor.execute(
                tool_name=tool_name,
                arguments=arguments,
            )
        except ToolError as error:
            raise AgentError(f"The selected tool {tool_name!r} failed during execution.") from error

    def _generate_final_response(
        self,
        user_message: str,
        conversation_context: str,
        tool_name: str,
        tool_output: str,
    ) -> str:
        """Return a safe response from a completed tool result."""
        del user_message
        del conversation_context

        cleaned_output = tool_output.strip()

        if not cleaned_output:
            raise AgentError("The selected tool returned an empty result.")

        logger.info(
            "Agent completed tool-assisted request. tool=%s response_length=%d",
            tool_name,
            len(cleaned_output),
        )

        return cleaned_output
