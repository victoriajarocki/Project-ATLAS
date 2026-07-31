"""Tests for persistent ATLAS conversation sessions."""

from pathlib import Path

import pytest

from atlas.conversations.database import (
    SQLiteConversationRepository,
)
from atlas.conversations.service import (
    ConversationService,
    ConversationValidationError,
)


@pytest.fixture
def conversation_service(
    tmp_path: Path,
) -> ConversationService:
    """Create an isolated service for each test."""
    repository = SQLiteConversationRepository(database_path=tmp_path / "conversations.db")

    service = ConversationService(repository)
    service.initialize()

    return service


def test_create_conversation(
    conversation_service: ConversationService,
) -> None:
    """The service should create conversations."""
    conversation = conversation_service.create_conversation("Rocket Planning")

    assert conversation.id > 0
    assert conversation.title == "Rocket Planning"


def test_get_or_create_latest_creates_first_chat(
    conversation_service: ConversationService,
) -> None:
    """A first conversation should be created automatically."""
    conversation = conversation_service.get_or_create_latest()

    assert conversation.title == "New conversation"


def test_messages_persist_in_conversation(
    conversation_service: ConversationService,
) -> None:
    """Messages should remain associated with their chat."""
    conversation = conversation_service.create_conversation("Testing")

    conversation_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content="Hello ATLAS.",
    )

    conversation_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content="Hello.",
    )

    messages = conversation_service.list_messages(conversation_id=conversation.id)

    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[0].content == "Hello ATLAS."
    assert messages[1].role == "assistant"


def test_recent_messages_are_chronological(
    conversation_service: ConversationService,
) -> None:
    """Recent messages should remain chronologically ordered."""
    conversation = conversation_service.create_conversation("Order Test")

    for number in range(1, 5):
        conversation_service.add_message(
            conversation_id=conversation.id,
            role="user",
            content=f"Message {number}",
        )

    messages = conversation_service.list_messages(
        conversation_id=conversation.id,
        limit=2,
    )

    assert [message.content for message in messages] == [
        "Message 3",
        "Message 4",
    ]


def test_rename_conversation(
    conversation_service: ConversationService,
) -> None:
    """A conversation should be renameable."""
    conversation = conversation_service.create_conversation("Old title")

    renamed = conversation_service.rename_conversation(
        conversation_id=conversation.id,
        title="New title",
    )

    updated = conversation_service.get_conversation(conversation.id)

    assert renamed is True
    assert updated is not None
    assert updated.title == "New title"


def test_empty_title_is_rejected_when_renaming(
    conversation_service: ConversationService,
) -> None:
    """An empty replacement title should be rejected."""
    conversation = conversation_service.create_conversation()

    with pytest.raises(ConversationValidationError):
        conversation_service.rename_conversation(
            conversation_id=conversation.id,
            title="   ",
        )


def test_model_context_contains_history(
    conversation_service: ConversationService,
) -> None:
    """Conversation history should be formatted for models."""
    conversation = conversation_service.create_conversation("Context Test")

    conversation_service.add_message(
        conversation_id=conversation.id,
        role="user",
        content="My rocket is called Specter.",
    )

    conversation_service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content="Understood.",
    )

    context = conversation_service.build_model_context(conversation_id=conversation.id)

    assert "Conversation history:" in context
    assert "User: My rocket is called Specter." in context
    assert "Assistant: Understood." in context
