"""Data models for the ATLAS file-system subsystem."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class FileSystemEntryType(StrEnum):
    """Describe the type of a file-system entry."""

    FILE = "file"
    DIRECTORY = "directory"


@dataclass(frozen=True)
class FileSystemEntry:
    """Describe a file or directory visible to ATLAS."""

    name: str
    path: Path
    entry_type: FileSystemEntryType
    size_bytes: int | None
    modified_at: datetime


@dataclass(frozen=True)
class FileReadResult:
    """Represent the result of reading a text file."""

    path: Path
    content: str
    character_count: int


@dataclass(frozen=True)
class FileWriteResult:
    """Represent the result of writing a text file."""

    path: Path
    character_count: int
    created: bool
