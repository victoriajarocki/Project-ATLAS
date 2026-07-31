"""Business logic for ATLAS persistent memory."""

from atlas.memory.database import SQLiteMemoryRepository
from atlas.memory.models import MemoryRecord


class MemoryValidationError(ValueError):
    """Raised when memory input does not satisfy validation rules."""


class MemoryService:
    """Manage persistent memories for ATLAS."""

    MAX_MEMORY_LENGTH = 2_000
    DEFAULT_CATEGORY = "general"
    DEFAULT_SOURCE = "user"

    def __init__(
        self,
        repository: SQLiteMemoryRepository,
    ) -> None:
        """Initialize the memory service."""
        self._repository = repository

    def initialize(self) -> None:
        """Initialize persistent memory storage."""
        self._repository.initialize()

    def remember(
        self,
        content: str,
        category: str = DEFAULT_CATEGORY,
        source: str = DEFAULT_SOURCE,
    ) -> MemoryRecord:
        """Validate and save a persistent memory."""
        cleaned_content = content.strip()
        cleaned_category = category.strip().lower()
        cleaned_source = source.strip().lower()

        if not cleaned_content:
            raise MemoryValidationError("Memory content cannot be empty.")

        if len(cleaned_content) > self.MAX_MEMORY_LENGTH:
            raise MemoryValidationError(
                f"Memory content cannot exceed {self.MAX_MEMORY_LENGTH} characters."
            )

        if not cleaned_category:
            raise MemoryValidationError("Memory category cannot be empty.")

        if not cleaned_source:
            raise MemoryValidationError("Memory source cannot be empty.")

        return self._repository.add(
            content=cleaned_content,
            category=cleaned_category,
            source=cleaned_source,
        )

    def get(self, memory_id: int) -> MemoryRecord | None:
        """Return one memory by ID."""
        return self._repository.get(memory_id)

    def list_memories(
        self,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        """Return recent persistent memories."""
        return self._repository.list_recent(limit=limit)

    def search_memories(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        """Search persistent memories using text matching."""
        return self._repository.search(
            query=query,
            limit=limit,
        )

    def forget(self, memory_id: int) -> bool:
        """Delete one persistent memory."""
        return self._repository.delete(memory_id)

    def forget_all(self) -> int:
        """Delete every persistent memory."""
        return self._repository.delete_all()

    def build_model_context(
        self,
        limit: int = 20,
    ) -> str:
        """Format recent memories for inclusion in a model request."""
        memories = self.list_memories(limit=limit)

        if not memories:
            return ""

        lines = ["Relevant persistent memories about the user and their projects:"]

        for memory in reversed(memories):
            lines.append(f"- [{memory.category}] {memory.content}")

        lines.append(
            "Use these memories only when relevant. "
            "Do not claim they came from the current message."
        )

        return "\n".join(lines)
