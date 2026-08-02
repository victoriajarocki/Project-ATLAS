"""Core application coordinator for Project ATLAS."""

import json
import logging
from time import perf_counter
from typing import Any

from atlas.agent.models import AgentPendingToolRequest
from atlas.agent.service import AgentService
from atlas.conversations.database import ConversationDatabaseError
from atlas.conversations.service import (
    ConversationService,
    ConversationValidationError,
)
from atlas.memory.database import MemoryDatabaseError
from atlas.memory.service import (
    MemoryService,
    MemoryValidationError,
)
from atlas.models.base import ModelProvider
from atlas.observability.logging import request_context
from atlas.permissions.models import (
    PendingToolRequest,
    PermissionDecision,
    PermissionEvaluation,
)
from atlas.permissions.service import PermissionService
from atlas.tools.base import (
    ToolError,
    ToolResult,
    ToolValidationError,
)
from atlas.tools.executor import ToolExecutor

logger = logging.getLogger(__name__)


class AtlasApp:
    """Coordinate user requests with ATLAS subsystems."""

    def __init__(
        self,
        model_provider: ModelProvider,
        memory_service: MemoryService | None = None,
        conversation_service: ConversationService | None = None,
        tool_executor: ToolExecutor | None = None,
        permission_service: PermissionService | None = None,
        agent_service: AgentService | None = None,
    ) -> None:
        """Initialize ATLAS with its configured subsystems."""
        self._model_provider = model_provider
        self._memory_service = memory_service
        self._conversation_service = conversation_service
        self._tool_executor = tool_executor
        self._permission_service = permission_service
        self._agent_service = agent_service

        self._active_conversation_id: int | None = None

        self._pending_tool_request: PendingToolRequest | None = None
        self._pending_permission_evaluation: PermissionEvaluation | None = None
        self._pending_agent_request: AgentPendingToolRequest | None = None

        if self._conversation_service is not None:
            conversation = self._conversation_service.get_or_create_latest()
            self._active_conversation_id = conversation.id

            logger.info(
                "Restored active conversation. conversation_id=%d",
                conversation.id,
            )

    @property
    def provider_name(self) -> str:
        """Return the active model provider name."""
        return self._model_provider.provider_name

    @property
    def memory_enabled(self) -> bool:
        """Report whether persistent memory is available."""
        return self._memory_service is not None

    @property
    def conversations_enabled(self) -> bool:
        """Report whether conversation sessions are available."""
        return self._conversation_service is not None

    @property
    def tools_enabled(self) -> bool:
        """Report whether the tool system is available."""
        return self._tool_executor is not None

    @property
    def permissions_enabled(self) -> bool:
        """Report whether permission controls are available."""
        return self._permission_service is not None

    @property
    def agent_enabled(self) -> bool:
        """Report whether model-directed agent behavior is available."""
        return self._agent_service is not None

    @property
    def active_conversation_id(self) -> int | None:
        """Return the active conversation ID."""
        return self._active_conversation_id

    @property
    def has_pending_tool_request(self) -> bool:
        """Report whether any tool request awaits confirmation."""
        return self._pending_tool_request is not None or self._pending_agent_request is not None

    def process_message(
        self,
        user_message: str,
    ) -> str:
        """Process one user message and return ATLAS's response."""
        with request_context() as request_id:
            started_at = perf_counter()
            cleaned_message = user_message.strip()

            logger.info(
                "Started processing user message. request_id=%s message_length=%d",
                request_id,
                len(cleaned_message),
            )

            try:
                if not cleaned_message:
                    logger.warning("Received an empty user message.")
                    return "I did not receive a message."

                command_response = self._process_command(cleaned_message)

                if command_response is not None:
                    logger.info("Processed message as an ATLAS command.")
                    return command_response

                if self.has_pending_tool_request:
                    return (
                        "A tool request is awaiting confirmation. "
                        "Use 'confirm yes' or 'confirm no' before "
                        "submitting another request."
                    )

                response = self._process_model_message(cleaned_message)

                logger.info(
                    "Model response generated successfully. response_length=%d",
                    len(response),
                )

                return response

            except Exception:
                logger.exception("ATLAS failed while processing a request.")
                raise

            finally:
                elapsed_seconds = perf_counter() - started_at

                logger.info(
                    "Completed request in %.3f seconds.",
                    elapsed_seconds,
                )

    def _process_command(
        self,
        message: str,
    ) -> str | None:
        """Process an ATLAS command when present."""
        lowered_message = message.lower()

        if lowered_message == "memories":
            return self._list_memories()

        if lowered_message.startswith("remember "):
            content = message[len("remember ") :]
            return self._remember(content)

        if lowered_message.startswith("forget "):
            identifier = message[len("forget ") :].strip()
            return self._forget(identifier)

        if lowered_message == "new chat":
            return self._new_conversation("New conversation")

        if lowered_message.startswith("new chat "):
            title = message[len("new chat ") :]
            return self._new_conversation(title)

        if lowered_message == "chats":
            return self._list_conversations()

        if lowered_message == "history":
            return self._show_history()

        if lowered_message.startswith("use chat "):
            identifier = message[len("use chat ") :].strip()
            return self._switch_conversation(identifier)

        if lowered_message.startswith("rename chat "):
            title = message[len("rename chat ") :]
            return self._rename_conversation(title)

        if lowered_message == "tools":
            return self._list_tools()

        if lowered_message == "confirm yes":
            return self._resolve_pending_tool(approved=True)

        if lowered_message == "confirm no":
            return self._resolve_pending_tool(approved=False)

        if lowered_message.startswith("confirm "):
            return "Confirmation must be either 'confirm yes' or 'confirm no'."

        if lowered_message.startswith("tool "):
            command = message[len("tool ") :]
            return self._execute_tool_command(command)

        return None

    def _process_model_message(
        self,
        user_message: str,
    ) -> str:
        """Store, contextualize, and process a normal message."""
        conversation_context = self._build_agent_context()

        self._store_conversation_message(
            role="user",
            content=user_message,
        )

        if self._agent_service is None:
            model_input = self._build_model_input(user_message)
            response = self._model_provider.generate_response(model_input)
            self._store_conversation_message(
                role="assistant",
                content=response,
            )
            return response

        result = self._agent_service.process_request(
            user_message=user_message,
            conversation_context=conversation_context,
        )

        if result.pending_request is not None:
            self._pending_agent_request = result.pending_request
            response = self._format_agent_confirmation(result.pending_request)
            self._store_conversation_message(
                role="assistant",
                content=response,
            )
            return response

        if result.response is None:
            raise RuntimeError("The agent returned neither a response nor a pending request.")

        self._store_conversation_message(
            role="assistant",
            content=result.response,
        )

        return result.response

    def _format_agent_confirmation(
        self,
        pending_request: AgentPendingToolRequest,
    ) -> str:
        """Format an agent-selected confirmation request."""
        evaluation = pending_request.evaluation

        return (
            f"Tool {evaluation.tool_name} requires "
            "confirmation.\n"
            f"Risk level: {evaluation.risk_level}.\n"
            f"Reason: {evaluation.reason}\n"
            "Use 'confirm yes' to approve or "
            "'confirm no' to deny."
        )

    def _list_tools(self) -> str:
        """Return a readable list of registered tools."""
        if self._tool_executor is None:
            return "The tool system is not currently available."

        definitions = self._tool_executor.registry.list_definitions()

        if not definitions:
            return "No tools are currently registered."

        lines = ["Registered tools:"]

        for definition in definitions:
            confirmation = (
                "confirmation required"
                if definition.requires_confirmation
                else "no confirmation required"
            )

            lines.append(
                f"- {definition.name} "
                f"[risk: {definition.risk_level}] "
                f"({confirmation}): "
                f"{definition.description}"
            )

        return "\n".join(lines)

    def _execute_tool_command(
        self,
        command: str,
    ) -> str:
        """Parse, validate, authorize, and execute a tool."""
        if self._tool_executor is None:
            return "The tool system is not currently available."

        if self.has_pending_tool_request:
            return (
                "Another tool request is already awaiting "
                "confirmation. Use 'confirm yes' or "
                "'confirm no' before submitting another "
                "confirmation-controlled tool request."
            )

        cleaned_command = command.strip()

        if not cleaned_command:
            return "Use: tool <tool name> <JSON arguments>"

        name_and_arguments = cleaned_command.split(maxsplit=1)
        tool_name = name_and_arguments[0]
        arguments_text = name_and_arguments[1] if len(name_and_arguments) == 2 else "{}"

        try:
            parsed_arguments: Any = json.loads(arguments_text)
        except json.JSONDecodeError as error:
            return f"Tool arguments must be valid JSON. JSON error: {error.msg}"

        if not isinstance(parsed_arguments, dict):
            return "Tool arguments must be a JSON object."

        try:
            tool = self._tool_executor.registry.get(tool_name)
        except ToolError as error:
            return f"The tool failed: {error}"

        try:
            self._tool_executor.validate_arguments(
                tool_name=tool.definition.name,
                arguments=parsed_arguments,
            )
        except ToolValidationError as error:
            return f"Tool input was invalid: {error}"

        if self._permission_service is None:
            logger.warning(
                "Executing tool without permission service. tool=%s",
                tool.definition.name,
            )

            return self._execute_authorized_tool(
                tool_name=tool.definition.name,
                arguments=parsed_arguments,
            )

        evaluation = self._permission_service.evaluate(tool.definition)

        if evaluation.decision is PermissionDecision.DENY:
            logger.warning(
                "Tool execution denied by policy. tool=%s risk=%s",
                evaluation.tool_name,
                evaluation.risk_level,
            )

            return f"Tool {evaluation.tool_name} was denied.\nReason: {evaluation.reason}"

        if evaluation.decision is PermissionDecision.CONFIRM:
            self._pending_tool_request = PendingToolRequest(
                tool_name=tool.definition.name,
                arguments=dict(parsed_arguments),
                risk_level=tool.definition.risk_level,
            )
            self._pending_permission_evaluation = evaluation

            logger.info(
                "Tool request is awaiting confirmation. tool=%s risk=%s",
                evaluation.tool_name,
                evaluation.risk_level,
            )

            return (
                f"Tool {evaluation.tool_name} requires "
                "confirmation.\n"
                f"Risk level: {evaluation.risk_level}.\n"
                f"Reason: {evaluation.reason}\n"
                "Use 'confirm yes' to approve or "
                "'confirm no' to deny."
            )

        return self._execute_authorized_tool(
            tool_name=tool.definition.name,
            arguments=parsed_arguments,
        )

    def _resolve_pending_tool(
        self,
        approved: bool,
    ) -> str:
        """Approve or deny a pending explicit or agent tool request."""
        if self._pending_agent_request is not None:
            return self._resolve_pending_agent_tool(approved=approved)

        pending_request = self._pending_tool_request
        evaluation = self._pending_permission_evaluation

        if pending_request is None or evaluation is None:
            self._clear_pending_tool_request()
            return "There is no pending tool request."

        if self._permission_service is not None:
            self._permission_service.record_confirmation(
                evaluation=evaluation,
                approved=approved,
            )

        self._clear_pending_tool_request()

        if not approved:
            logger.info(
                "Pending tool execution denied by user. tool=%s risk=%s",
                pending_request.tool_name,
                pending_request.risk_level,
            )
            return f"Tool {pending_request.tool_name} execution was denied."

        logger.info(
            "Pending tool execution approved by user. tool=%s risk=%s",
            pending_request.tool_name,
            pending_request.risk_level,
        )

        return self._execute_authorized_tool(
            tool_name=pending_request.tool_name,
            arguments=pending_request.arguments,
        )

    def _resolve_pending_agent_tool(
        self,
        approved: bool,
    ) -> str:
        """Resolve a model-selected pending tool request."""
        pending_request = self._pending_agent_request

        if pending_request is None:
            return "There is no pending tool request."

        self._pending_agent_request = None

        if self._agent_service is None:
            return "The agent system is not currently available."

        if approved:
            response = self._agent_service.complete_confirmed_request(pending_request)
        else:
            response = self._agent_service.deny_confirmed_request(pending_request)

        self._store_conversation_message(
            role="assistant",
            content=response,
        )

        return response

    def _clear_pending_tool_request(self) -> None:
        """Clear explicit confirmation state."""
        self._pending_tool_request = None
        self._pending_permission_evaluation = None

    def _execute_authorized_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> str:
        """Execute a tool after authorization succeeds."""
        if self._tool_executor is None:
            return "The tool system is not currently available."

        try:
            result = self._tool_executor.execute(
                tool_name=tool_name,
                arguments=arguments,
            )
        except ToolValidationError as error:
            return f"Tool input was invalid: {error}"
        except ToolError as error:
            return f"The tool failed: {error}"

        return self._format_tool_result(result)

    @staticmethod
    def _format_tool_result(
        result: ToolResult,
    ) -> str:
        """Format a structured tool result for the user."""
        if not result.success:
            error_message = result.error or ("The tool did not provide an error message.")
            return f"Tool {result.tool_name} failed: {error_message}"

        return f"Tool {result.tool_name} result: {result.output}"

    def _store_conversation_message(
        self,
        role: str,
        content: str,
    ) -> None:
        """Store one conversation message when sessions are enabled."""
        if self._conversation_service is None or self._active_conversation_id is None:
            return

        self._conversation_service.add_message(
            conversation_id=self._active_conversation_id,
            role=role,
            content=content,
        )

        logger.debug(
            "Stored %s message. conversation_id=%d",
            role,
            self._active_conversation_id,
        )

    def _remember(
        self,
        content: str,
    ) -> str:
        """Save a user-requested memory."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memory = self._memory_service.remember(content)
        except MemoryValidationError as error:
            logger.warning("Memory validation failed.")
            return f"I could not save that memory: {error}"
        except MemoryDatabaseError as error:
            logger.exception("The memory database failed while saving a memory.")
            return f"The memory database failed: {error}"

        logger.info(
            "Created persistent memory. memory_id=%d",
            memory.id,
        )

        return f"I will remember that. Memory ID: {memory.id}."

    def _list_memories(self) -> str:
        """Return a readable list of stored memories."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memories = self._memory_service.list_memories()
        except MemoryDatabaseError as error:
            logger.exception("The memory database failed while listing memories.")
            return f"The memory database failed: {error}"

        if not memories:
            return "I do not have any persistent memories yet."

        lines = ["Persistent memories:"]

        for memory in memories:
            lines.append(f"[{memory.id}] ({memory.category}) {memory.content}")

        logger.info(
            "Listed persistent memories. memory_count=%d",
            len(memories),
        )

        return "\n".join(lines)

    def _forget(
        self,
        identifier: str,
    ) -> str:
        """Delete a memory using its numeric ID."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memory_id = int(identifier)
        except ValueError:
            logger.warning("Forget command received a nonnumeric memory ID.")
            return "Use a numeric memory ID, such as: forget 3"

        if memory_id < 1:
            return "Memory IDs must be positive integers."

        try:
            deleted = self._memory_service.forget(memory_id)
        except MemoryDatabaseError as error:
            logger.exception("The memory database failed while deleting a memory.")
            return f"The memory database failed: {error}"

        if not deleted:
            logger.warning(
                "Requested memory was not found. memory_id=%d",
                memory_id,
            )
            return f"I could not find memory {memory_id}."

        logger.info(
            "Deleted persistent memory. memory_id=%d",
            memory_id,
        )

        return f"Memory {memory_id} was deleted."

    def _new_conversation(
        self,
        title: str,
    ) -> str:
        """Create and activate a conversation."""
        if self._conversation_service is None:
            return "Conversation sessions are not available."

        try:
            conversation = self._conversation_service.create_conversation(title=title)
        except ConversationValidationError as error:
            logger.warning("Conversation creation validation failed.")
            return f"I could not create that chat: {error}"
        except ConversationDatabaseError as error:
            logger.exception("The conversation database failed while creating a conversation.")
            return f"The conversation database failed: {error}"

        self._active_conversation_id = conversation.id

        logger.info(
            "Created conversation. conversation_id=%d",
            conversation.id,
        )

        return f"Created chat {conversation.id}: {conversation.title}"

    def _list_conversations(self) -> str:
        """Return a readable list of conversations."""
        if self._conversation_service is None:
            return "Conversation sessions are not available."

        try:
            conversations = self._conversation_service.list_conversations()
        except ConversationDatabaseError as error:
            logger.exception("The conversation database failed while listing conversations.")
            return f"The conversation database failed: {error}"

        if not conversations:
            return "There are no saved conversations."

        lines = ["Saved conversations:"]

        for conversation in conversations:
            active_marker = "*" if conversation.id == self._active_conversation_id else " "

            lines.append(f"{active_marker} [{conversation.id}] {conversation.title}")

        logger.info(
            "Listed conversations. conversation_count=%d",
            len(conversations),
        )

        return "\n".join(lines)

    def _switch_conversation(
        self,
        identifier: str,
    ) -> str:
        """Switch to a conversation by numeric ID."""
        if self._conversation_service is None:
            return "Conversation sessions are not available."

        try:
            conversation_id = int(identifier)
        except ValueError:
            logger.warning("Use-chat command received a nonnumeric chat ID.")
            return "Use a numeric chat ID, such as: use chat 2"

        conversation = self._conversation_service.get_conversation(conversation_id)

        if conversation is None:
            logger.warning(
                "Requested conversation was not found. conversation_id=%d",
                conversation_id,
            )
            return f"I could not find chat {conversation_id}."

        self._active_conversation_id = conversation.id

        logger.info(
            "Switched active conversation. conversation_id=%d",
            conversation.id,
        )

        return f"Switched to chat {conversation.id}: {conversation.title}"

    def _rename_conversation(
        self,
        title: str,
    ) -> str:
        """Rename the active conversation."""
        if self._conversation_service is None or self._active_conversation_id is None:
            return "There is no active conversation to rename."

        try:
            renamed = self._conversation_service.rename_conversation(
                conversation_id=self._active_conversation_id,
                title=title,
            )
        except ConversationValidationError as error:
            logger.warning(
                "Conversation rename validation failed. conversation_id=%d",
                self._active_conversation_id,
            )
            return f"I could not rename that chat: {error}"
        except ConversationDatabaseError as error:
            logger.exception("The conversation database failed while renaming a conversation.")
            return f"The conversation database failed: {error}"

        if not renamed:
            logger.warning(
                "Active conversation could not be found during rename. conversation_id=%d",
                self._active_conversation_id,
            )
            return "The active conversation could not be found."

        logger.info(
            "Renamed conversation. conversation_id=%d",
            self._active_conversation_id,
        )

        return f"Renamed chat {self._active_conversation_id} to: {title.strip()}"

    def _show_history(self) -> str:
        """Display recent messages in the active conversation."""
        if self._conversation_service is None or self._active_conversation_id is None:
            return "There is no active conversation."

        try:
            messages = self._conversation_service.list_messages(
                conversation_id=self._active_conversation_id,
                limit=20,
            )
        except ConversationDatabaseError as error:
            logger.exception("The conversation database failed while retrieving chat history.")
            return f"The conversation database failed: {error}"

        if not messages:
            return "The active conversation has no messages yet."

        lines = [f"History for chat {self._active_conversation_id}:"]

        for message in messages:
            role_name = message.role.capitalize()
            lines.append(f"{role_name}: {message.content}")

        logger.info(
            "Displayed conversation history. conversation_id=%d message_count=%d",
            self._active_conversation_id,
            len(messages),
        )

        return "\n".join(lines)

    def _build_agent_context(self) -> str:
        """Build memory and conversation context for the agent."""
        sections: list[str] = []

        if self._memory_service is not None:
            try:
                memory_context = self._memory_service.build_model_context()
            except MemoryDatabaseError:
                logger.exception("Could not build persistent memory context.")
                memory_context = ""

            if memory_context:
                sections.append(memory_context)

        if self._conversation_service is not None and self._active_conversation_id is not None:
            try:
                conversation_context = self._conversation_service.build_model_context(
                    conversation_id=self._active_conversation_id,
                    limit=20,
                )
            except ConversationDatabaseError:
                logger.exception(
                    "Could not build conversation context. conversation_id=%d",
                    self._active_conversation_id,
                )
                conversation_context = ""

            if conversation_context:
                sections.append(conversation_context)

        return "\n\n".join(sections)

    def _build_model_input(
        self,
        user_message: str,
    ) -> str:
        """Combine legacy context with a normal user message."""
        context = self._build_agent_context()

        if not context:
            return user_message

        return f"{context}\n\nUser: {user_message}"
