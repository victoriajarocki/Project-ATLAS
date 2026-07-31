"""Business logic for persistent ATLAS conversations."""

from atlas.conversations.database import (
    SQLiteConversationRepository,
)
from atlas.conversations.models import (
    ConversationRecord,
    MessageRecord,
)


class ConversationValidationError(ValueError):
    """Raised when conversation input is invalid."""


class ConversationService:
    """Manage persistent conversations and their messages."""

    DEFAULT_TITLE = "New conversation"
    MAX_TITLE_LENGTH = 120
    MAX_MESSAGE_LENGTH = 20_000
    ALLOWED_ROLES = {"user", "assistant", "system"}

    def __init__(
        self,
        repository: SQLiteConversationRepository,
    ) -> None:
        """Initialize the conversation service."""
        self._repository = repository

    def initialize(self) -> None:
        """Initialize conversation storage."""
        self._repository.initialize()

    def create_conversation(
        self,
        title: str = DEFAULT_TITLE,
    ) -> ConversationRecord:
        """Validate and create a conversation."""
        cleaned_title = title.strip()

        if not cleaned_title:
            cleaned_title = self.DEFAULT_TITLE

        if len(cleaned_title) > self.MAX_TITLE_LENGTH:
            raise ConversationValidationError(
                f"Conversation titles cannot exceed {self.MAX_TITLE_LENGTH} characters."
            )

        return self._repository.create_conversation(cleaned_title)

    def get_or_create_latest(
        self,
    ) -> ConversationRecord:
        """Return the latest conversation or create one."""
        conversation = self._repository.get_latest_conversation()

        if conversation is not None:
            return conversation

        return self.create_conversation()

    def get_conversation(
        self,
        conversation_id: int,
    ) -> ConversationRecord | None:
        """Return a conversation by ID."""
        return self._repository.get_conversation(conversation_id)

    def list_conversations(
        self,
        limit: int = 20,
    ) -> list[ConversationRecord]:
        """Return recently active conversations."""
        return self._repository.list_conversations(limit=limit)

    def rename_conversation(
        self,
        conversation_id: int,
        title: str,
    ) -> bool:
        """Validate and rename a conversation."""
        cleaned_title = title.strip()

        if not cleaned_title:
            raise ConversationValidationError("Conversation title cannot be empty.")

        if len(cleaned_title) > self.MAX_TITLE_LENGTH:
            raise ConversationValidationError(
                f"Conversation titles cannot exceed {self.MAX_TITLE_LENGTH} characters."
            )

        return self._repository.rename_conversation(
            conversation_id=conversation_id,
            title=cleaned_title,
        )

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> MessageRecord:
        """Validate and store a conversation message."""
        cleaned_role = role.strip().lower()
        cleaned_content = content.strip()

        if cleaned_role not in self.ALLOWED_ROLES:
            raise ConversationValidationError(f"Unsupported message role: {cleaned_role!r}.")

        if not cleaned_content:
            raise ConversationValidationError("Message content cannot be empty.")

        if len(cleaned_content) > self.MAX_MESSAGE_LENGTH:
            raise ConversationValidationError(
                f"Messages cannot exceed {self.MAX_MESSAGE_LENGTH} characters."
            )

        return self._repository.add_message(
            conversation_id=conversation_id,
            role=cleaned_role,
            content=cleaned_content,
        )

    def list_messages(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> list[MessageRecord]:
        """Return recent messages in chronological order."""
        return self._repository.list_messages(
            conversation_id=conversation_id,
            limit=limit,
        )

    def build_model_context(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> str:
        """Format recent messages for a model request."""
        messages = self.list_messages(
            conversation_id=conversation_id,
            limit=limit,
        )

        if not messages:
            return ""

        lines = [
            "Conversation history:",
        ]

        for message in messages:
            role_name = {
                "user": "User",
                "assistant": "Assistant",
                "system": "System",
            }.get(message.role, message.role.title())

            lines.append(f"{role_name}: {message.content}")

        lines.append(
            "Respond to the latest user message while using earlier messages only when relevant."
        )

        return "\n".join(lines)
