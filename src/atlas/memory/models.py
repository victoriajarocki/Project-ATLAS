"""Data models used by the ATLAS memory system."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MemoryRecord:
    """Represent one persistent ATLAS memory."""

    id: int
    content: str
    category: str
    source: str
    created_at: datetime
    updated_at: datetime
