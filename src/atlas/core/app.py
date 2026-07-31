"""Core application coordinator for Project ATLAS."""

import logging
from time import perf_counter

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

logger = logging.getLogger(__name__)


class AtlasApp:
    """Coordinate user requests with ATLAS subsystems."""

    def __init__(
        self,
        model_provider: ModelProvider,
        memory_service: MemoryService | None = None,
        conversation_service: ConversationService | None = None,
    ) -> None:
        """Initialize ATLAS with its configured subsystems."""
        self._model_provider = model_provider
        self._memory_service = memory_service
        self._conversation_service = conversation_service
        self._active_conversation_id: int | None = None

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
    def active_conversation_id(self) -> int | None:
        """Return the active conversation ID."""
        return self._active_conversation_id

    def process_message(self, user_message: str) -> str:
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

        return None

    def _process_model_message(
        self,
        user_message: str,
    ) -> str:
        """Store, contextualize, and process a normal message."""
        if self._conversation_service is not None and self._active_conversation_id is not None:
            self._conversation_service.add_message(
                conversation_id=self._active_conversation_id,
                role="user",
                content=user_message,
            )

            logger.debug(
                "Stored user message. conversation_id=%d",
                self._active_conversation_id,
            )

        model_input = self._build_model_input(user_message)
        response = self._model_provider.generate_response(model_input)

        if self._conversation_service is not None and self._active_conversation_id is not None:
            self._conversation_service.add_message(
                conversation_id=self._active_conversation_id,
                role="assistant",
                content=response,
            )

            logger.debug(
                "Stored assistant message. conversation_id=%d",
                self._active_conversation_id,
            )

        return response

    def _remember(self, content: str) -> str:
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

    def _forget(self, identifier: str) -> str:
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

    def _new_conversation(self, title: str) -> str:
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

    def _rename_conversation(self, title: str) -> str:
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

    def _build_model_input(
        self,
        user_message: str,
    ) -> str:
        """Combine memory and conversation context."""
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
                    conversation_id=(self._active_conversation_id),
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

        if not sections:
            return user_message

        return "\n\n".join(sections)
