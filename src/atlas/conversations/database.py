"""SQLite persistence layer for ATLAS conversation sessions."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from atlas.conversations.models import ConversationRecord, MessageRecord


class ConversationDatabaseError(RuntimeError):
    """Raised when a conversation database operation fails."""


class SQLiteConversationRepository:
    """Store conversations and messages using SQLite."""

    def __init__(self, database_path: Path) -> None:
        """Initialize the repository."""
        self._database_path = database_path

    @property
    def database_path(self) -> Path:
        """Return the configured database path."""
        return self._database_path

    def initialize(self) -> None:
        """Create conversation tables and indexes when necessary."""
        try:
            self._database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (conversation_id)
                            REFERENCES conversations(id)
                            ON DELETE CASCADE
                    )
                    """
                )

                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    index_conversations_updated_at
                    ON conversations(updated_at)
                    """
                )

                connection.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    index_conversation_messages_conversation_id
                    ON conversation_messages(conversation_id)
                    """
                )
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not initialize conversation database: {error}"
            ) from error

    def create_conversation(
        self,
        title: str,
    ) -> ConversationRecord:
        """Create and return a conversation."""
        timestamp = datetime.now(UTC)

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO conversations (
                        title,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        title,
                        timestamp.isoformat(),
                        timestamp.isoformat(),
                    ),
                )

                conversation_id = cursor.lastrowid
        except sqlite3.Error as error:
            raise ConversationDatabaseError(f"Could not create conversation: {error}") from error

        if conversation_id is None:
            raise ConversationDatabaseError("The database did not return a conversation ID.")

        return ConversationRecord(
            id=conversation_id,
            title=title,
            created_at=timestamp,
            updated_at=timestamp,
        )

    def get_conversation(
        self,
        conversation_id: int,
    ) -> ConversationRecord | None:
        """Return a conversation by ID."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        title,
                        created_at,
                        updated_at
                    FROM conversations
                    WHERE id = ?
                    """,
                    (conversation_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not retrieve conversation {conversation_id}: {error}"
            ) from error

        if row is None:
            return None

        return self._row_to_conversation(row)

    def get_latest_conversation(
        self,
    ) -> ConversationRecord | None:
        """Return the most recently active conversation."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        id,
                        title,
                        created_at,
                        updated_at
                    FROM conversations
                    ORDER BY updated_at DESC, id DESC
                    LIMIT 1
                    """
                ).fetchone()
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not retrieve the latest conversation: {error}"
            ) from error

        if row is None:
            return None

        return self._row_to_conversation(row)

    def list_conversations(
        self,
        limit: int = 20,
    ) -> list[ConversationRecord]:
        """Return recently active conversations."""
        if limit < 1:
            return []

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        title,
                        created_at,
                        updated_at
                    FROM conversations
                    ORDER BY updated_at DESC, id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        except sqlite3.Error as error:
            raise ConversationDatabaseError(f"Could not list conversations: {error}") from error

        return [self._row_to_conversation(row) for row in rows]

    def rename_conversation(
        self,
        conversation_id: int,
        title: str,
    ) -> bool:
        """Rename a conversation and report whether it existed."""
        timestamp = datetime.now(UTC)

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    UPDATE conversations
                    SET title = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        title,
                        timestamp.isoformat(),
                        conversation_id,
                    ),
                )
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not rename conversation {conversation_id}: {error}"
            ) from error

        return cursor.rowcount > 0

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
    ) -> MessageRecord:
        """Store and return a conversation message."""
        timestamp = datetime.now(UTC)

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO conversation_messages (
                        conversation_id,
                        role,
                        content,
                        created_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        conversation_id,
                        role,
                        content,
                        timestamp.isoformat(),
                    ),
                )

                message_id = cursor.lastrowid

                connection.execute(
                    """
                    UPDATE conversations
                    SET updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        timestamp.isoformat(),
                        conversation_id,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ConversationDatabaseError(
                f"Conversation {conversation_id} does not exist."
            ) from error
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not add conversation message: {error}"
            ) from error

        if message_id is None:
            raise ConversationDatabaseError("The database did not return a message ID.")

        return MessageRecord(
            id=message_id,
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=timestamp,
        )

    def list_messages(
        self,
        conversation_id: int,
        limit: int = 20,
    ) -> list[MessageRecord]:
        """Return recent messages in chronological order."""
        if limit < 1:
            return []

        try:
            with self._connect() as connection:
                rows = connection.execute(
                    """
                    SELECT
                        id,
                        conversation_id,
                        role,
                        content,
                        created_at
                    FROM (
                        SELECT
                            id,
                            conversation_id,
                            role,
                            content,
                            created_at
                        FROM conversation_messages
                        WHERE conversation_id = ?
                        ORDER BY id DESC
                        LIMIT ?
                    )
                    ORDER BY id ASC
                    """,
                    (
                        conversation_id,
                        limit,
                    ),
                ).fetchall()
        except sqlite3.Error as error:
            raise ConversationDatabaseError(
                f"Could not list messages for conversation {conversation_id}: {error}"
            ) from error

        return [self._row_to_message(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        """Create a configured SQLite connection."""
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _row_to_conversation(
        row: sqlite3.Row,
    ) -> ConversationRecord:
        """Convert a SQLite row into a conversation record."""
        return ConversationRecord(
            id=int(row["id"]),
            title=str(row["title"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
            updated_at=datetime.fromisoformat(str(row["updated_at"])),
        )

    @staticmethod
    def _row_to_message(
        row: sqlite3.Row,
    ) -> MessageRecord:
        """Convert a SQLite row into a message record."""
        return MessageRecord(
            id=int(row["id"]),
            conversation_id=int(row["conversation_id"]),
            role=str(row["role"]),
            content=str(row["content"]),
            created_at=datetime.fromisoformat(str(row["created_at"])),
        )
