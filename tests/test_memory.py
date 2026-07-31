"""Tests for the ATLAS persistent memory subsystem."""

from pathlib import Path

import pytest

from atlas.memory.database import SQLiteMemoryRepository
from atlas.memory.service import (
    MemoryService,
    MemoryValidationError,
)


@pytest.fixture
def memory_service(
    tmp_path: Path,
) -> MemoryService:
    """Create an isolated memory service for each test."""
    repository = SQLiteMemoryRepository(database_path=tmp_path / "test_memory.db")

    service = MemoryService(repository)
    service.initialize()

    return service


def test_remember_persists_memory(
    memory_service: MemoryService,
) -> None:
    """The service should save and retrieve a memory."""
    created = memory_service.remember("My L2 rocket is named Wraith.")

    retrieved = memory_service.get(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.content == ("My L2 rocket is named Wraith.")
    assert retrieved.category == "general"
    assert retrieved.source == "user"


def test_list_memories_returns_newest_first(
    memory_service: MemoryService,
) -> None:
    """Recent memories should be listed newest first."""
    first = memory_service.remember("First memory.")
    second = memory_service.remember("Second memory.")

    memories = memory_service.list_memories()

    assert [memory.id for memory in memories] == [
        second.id,
        first.id,
    ]


def test_search_memories_matches_content(
    memory_service: MemoryService,
) -> None:
    """Memory search should find matching text."""
    memory_service.remember("Project ATLAS uses a modular architecture.")
    memory_service.remember("Wraith is the L2 rocket.")

    results = memory_service.search_memories("atlas")

    assert len(results) == 1
    assert "ATLAS" in results[0].content


def test_forget_deletes_memory(
    memory_service: MemoryService,
) -> None:
    """The service should delete a selected memory."""
    memory = memory_service.remember("Temporary information.")

    deleted = memory_service.forget(memory.id)

    assert deleted is True
    assert memory_service.get(memory.id) is None


def test_forget_missing_memory_returns_false(
    memory_service: MemoryService,
) -> None:
    """Deleting an unknown memory should return false."""
    deleted = memory_service.forget(999)

    assert deleted is False


def test_empty_memory_is_rejected(
    memory_service: MemoryService,
) -> None:
    """The service should reject empty memories."""
    with pytest.raises(MemoryValidationError):
        memory_service.remember("   ")


def test_model_context_contains_memories(
    memory_service: MemoryService,
) -> None:
    """The service should format memories for the model."""
    memory_service.remember(
        "The user's L2 rocket is named Wraith.",
        category="project",
    )

    context = memory_service.build_model_context()

    assert "Relevant persistent memories" in context
    assert "[project]" in context
    assert "Wraith" in context
