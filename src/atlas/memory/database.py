"""SQLite persistence layer for the ATLAS memory system."""

import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from atlas.memory.models import MemoryRecord


class MemoryDatabaseError(RuntimeError):
    """Raised when the persistent memory database operation fails."""


class SQLiteMemoryRepository:
    """Store and retrieve persistent memories using SQLite."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the repository with a local database path."""
        self._database_path = database_path

    @property
    def database_path(self) -> Path:
        """Return the configured database path."""
        return self._database_path

    def initialize(self) -> None:
        """Create the database and memory table when necessary."""
        try:
            self._database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        category TEXT NOT NULL,
                        source TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    index_memories_created_at
                    ON memories(created_at)
                    """
                )
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not initialize memory database: {error}") from error

    def add(
        self,
        content: str,
        category: str,
        source: str,
    ) -> MemoryRecord:
        """Insert and return a persistent memory."""
        timestamp = datetime.now(UTC)

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO memories (
                        content,
                        category,
                        source,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        content,
                        category,
                        source,
                        timestamp.isoformat(),
                        timestamp.isoformat(),
                    ),
                )

                memory_id = cursor.lastrowid

                if memory_id is None:
                    raise MemoryDatabaseError("The database did not return a memory ID.")
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not add memory: {error}") from error

        return MemoryRecord(
            id=memory_id,
            content=content,
            category=category,
            source=source,
            created_at=timestamp,
            updated_at=timestamp,
        )

    def get(self, memory_id: int) -> MemoryRecord | None:
        """Return one memory by ID."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        content,
                        category,
                        source,
                        created_at,
                        updated_at
                    FROM memories
                    WHERE id = ?
                    """,
                    (memory_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not retrieve memory {memory_id}: {error}") from error

        if row is None:
            return None

        return self._row_to_record(row)

    def list_recent(self, limit: int = 20) -> list[MemoryRecord]:
        """Return the most recently created memories."""
        if limit < 1:
            return []

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        content,
                        category,
                        source,
                        created_at,
                        updated_at
                    FROM memories
                    ORDER BY created_at DESC, id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not list memories: {error}") from error

        return [self._row_to_record(row) for row in rows]

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MemoryRecord]:
        """Find memories containing the supplied text."""
        cleaned_query = query.strip()

        if not cleaned_query or limit < 1:
            return []

        search_pattern = f"%{cleaned_query}%"

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        content,
                        category,
                        source,
                        created_at,
                        updated_at
                    FROM memories
                    WHERE content LIKE ? COLLATE NOCASE
                    ORDER BY updated_at DESC, id DESC
                    LIMIT ?
                    """,
                    (search_pattern, limit),
                ).fetchall()
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not search memories: {error}") from error

        return [self._row_to_record(row) for row in rows]

    def delete(self, memory_id: int) -> bool:
        """Delete a memory and report whether it existed."""
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    "DELETE FROM memories WHERE id = ?",
                    (memory_id,),
                )
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not delete memory {memory_id}: {error}") from error

        return cursor.rowcount > 0

    def delete_all(self) -> int:
        """Delete all memories and return the number removed."""
        try:
            with self._connect() as connection:
                cursor = connection.execute("DELETE FROM memories")
        except sqlite3.Error as error:
            raise MemoryDatabaseError(f"Could not delete all memories: {error}") from error

        return cursor.rowcount

    def _connect(self) -> sqlite3.Connection:
        """Create a configured SQLite connection."""
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> MemoryRecord:
        """Convert a SQLite row into a memory record."""
        required_columns: Sequence[str] = (
            "id",
            "content",
            "category",
            "source",
            "created_at",
            "updated_at",
        )

        for column in required_columns:
            if column not in row.keys():
                raise MemoryDatabaseError(f"Memory database row is missing column {column!r}.")

        return MemoryRecord(
            id=int(row["id"]),
            content=str(row["content"]),
            category=str(row["category"]),
            source=str(row["source"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
        )
