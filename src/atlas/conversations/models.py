"""Data models used by ATLAS conversation sessions."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConversationRecord:
    """Represent one persistent conversation."""

    id: int
    title: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class MessageRecord:
    """Represent one message within a conversation."""

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
