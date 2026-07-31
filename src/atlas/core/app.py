"""Core application coordinator for Project ATLAS."""

from atlas.memory.database import MemoryDatabaseError
from atlas.memory.service import (
    MemoryService,
    MemoryValidationError,
)
from atlas.models.base import ModelProvider


class AtlasApp:
    """Coordinate user requests with ATLAS subsystems."""

    def __init__(
        self,
        model_provider: ModelProvider,
        memory_service: MemoryService | None = None,
    ) -> None:
        """Initialize ATLAS with its configured subsystems."""
        self._model_provider = model_provider
        self._memory_service = memory_service

    @property
    def provider_name(self) -> str:
        """Return the active model provider name."""
        return self._model_provider.provider_name

    @property
    def memory_enabled(self) -> bool:
        """Report whether persistent memory is available."""
        return self._memory_service is not None

    def process_message(self, user_message: str) -> str:
        """Process one user message and return ATLAS's response."""
        cleaned_message = user_message.strip()

        if not cleaned_message:
            return "I did not receive a message."

        command_response = self._process_memory_command(cleaned_message)

        if command_response is not None:
            return command_response

        model_input = self._build_model_input(cleaned_message)

        return self._model_provider.generate_response(model_input)

    def _process_memory_command(
        self,
        message: str,
    ) -> str | None:
        """Process an explicit memory command when present."""
        lowered_message = message.lower()

        if lowered_message == "memories":
            return self._list_memories()

        if lowered_message.startswith("remember "):
            content = message[len("remember ") :]
            return self._remember(content)

        if lowered_message.startswith("forget "):
            identifier = message[len("forget ") :].strip()
            return self._forget(identifier)

        return None

    def _remember(self, content: str) -> str:
        """Save a user-requested memory."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memory = self._memory_service.remember(content)
        except MemoryValidationError as error:
            return f"I could not save that memory: {error}"
        except MemoryDatabaseError as error:
            return f"The memory database failed: {error}"

        return f"I will remember that. Memory ID: {memory.id}."

    def _list_memories(self) -> str:
        """Return a readable list of stored memories."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memories = self._memory_service.list_memories()
        except MemoryDatabaseError as error:
            return f"The memory database failed: {error}"

        if not memories:
            return "I do not have any persistent memories yet."

        lines = ["Persistent memories:"]

        for memory in memories:
            lines.append(f"[{memory.id}] ({memory.category}) {memory.content}")

        return "\n".join(lines)

    def _forget(self, identifier: str) -> str:
        """Delete a memory using its numeric ID."""
        if self._memory_service is None:
            return "Persistent memory is not currently available."

        try:
            memory_id = int(identifier)
        except ValueError:
            return "Use a numeric memory ID, such as: forget 3"

        if memory_id < 1:
            return "Memory IDs must be positive integers."

        try:
            deleted = self._memory_service.forget(memory_id)
        except MemoryDatabaseError as error:
            return f"The memory database failed: {error}"

        if not deleted:
            return f"I could not find memory {memory_id}."

        return f"Memory {memory_id} was deleted."

    def _build_model_input(self, user_message: str) -> str:
        """Combine relevant persistent memory with a user message."""
        if self._memory_service is None:
            return user_message

        try:
            memory_context = self._memory_service.build_model_context()
        except MemoryDatabaseError:
            return user_message

        if not memory_context:
            return user_message

        return f"{memory_context}\n\nCurrent user message:\n{user_message}"
