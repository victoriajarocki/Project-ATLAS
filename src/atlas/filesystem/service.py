"""Scoped file-system operations for Project ATLAS."""

import logging
from datetime import datetime
from pathlib import Path

from atlas.filesystem.exceptions import (
    FileSystemOperationError,
    FileSystemValidationError,
)
from atlas.filesystem.models import (
    FileReadResult,
    FileSystemEntry,
    FileSystemEntryType,
    FileWriteResult,
)
from atlas.filesystem.paths import ScopedPathResolver

logger = logging.getLogger(__name__)


class FileSystemService:
    """Perform validated operations inside allowed directories."""

    DEFAULT_MAX_READ_BYTES = 1_000_000
    DEFAULT_MAX_WRITE_CHARACTERS = 1_000_000

    def __init__(
        self,
        path_resolver: ScopedPathResolver,
        max_read_bytes: int = DEFAULT_MAX_READ_BYTES,
        max_write_characters: int = DEFAULT_MAX_WRITE_CHARACTERS,
    ) -> None:
        """Initialize the scoped file-system service."""
        if max_read_bytes < 1:
            raise FileSystemValidationError("The maximum read size must be positive.")

        if max_write_characters < 1:
            raise FileSystemValidationError("The maximum write size must be positive.")

        self._path_resolver = path_resolver
        self._max_read_bytes = max_read_bytes
        self._max_write_characters = max_write_characters

    @property
    def allowed_directories(self) -> tuple[Path, ...]:
        """Return the configured allowed directories."""
        return self._path_resolver.allowed_directories

    def list_directory(
        self,
        requested_path: str = ".",
    ) -> list[FileSystemEntry]:
        """List visible entries in a scoped directory."""
        path = self._path_resolver.resolve(requested_path)

        if not path.exists():
            raise FileSystemValidationError(f"Directory does not exist: {requested_path}")

        if not path.is_dir():
            raise FileSystemValidationError(f"Path is not a directory: {requested_path}")

        try:
            children = sorted(
                path.iterdir(),
                key=lambda child: (
                    not child.is_dir(),
                    child.name.lower(),
                ),
            )

            entries = [self._build_entry(child) for child in children]
        except OSError as error:
            raise FileSystemOperationError(f"Could not list directory: {requested_path}") from error

        logger.info(
            "Listed scoped directory. path=%s entry_count=%d",
            path,
            len(entries),
        )

        return entries

    def get_info(
        self,
        requested_path: str,
    ) -> FileSystemEntry:
        """Return metadata for a scoped file or directory."""
        path = self._path_resolver.resolve(requested_path)

        if not path.exists():
            raise FileSystemValidationError(f"Path does not exist: {requested_path}")

        try:
            entry = self._build_entry(path)
        except OSError as error:
            raise FileSystemOperationError(f"Could not inspect path: {requested_path}") from error

        logger.info(
            "Inspected scoped path. path=%s type=%s",
            path,
            entry.entry_type,
        )

        return entry

    def read_text_file(
        self,
        requested_path: str,
    ) -> FileReadResult:
        """Read a UTF-8 text file inside the allowed scope."""
        path = self._path_resolver.resolve(requested_path)

        if not path.exists():
            raise FileSystemValidationError(f"File does not exist: {requested_path}")

        if not path.is_file():
            raise FileSystemValidationError(f"Path is not a file: {requested_path}")

        try:
            size_bytes = path.stat().st_size
        except OSError as error:
            raise FileSystemOperationError(f"Could not inspect file: {requested_path}") from error

        if size_bytes > self._max_read_bytes:
            raise FileSystemValidationError(
                "The requested file exceeds the configured "
                f"read limit of {self._max_read_bytes} bytes."
            )

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise FileSystemValidationError(
                "The requested file is not valid UTF-8 text."
            ) from error
        except OSError as error:
            raise FileSystemOperationError(f"Could not read file: {requested_path}") from error

        logger.info(
            "Read scoped text file. path=%s size_bytes=%d character_count=%d",
            path,
            size_bytes,
            len(content),
        )

        return FileReadResult(
            path=path,
            content=content,
            character_count=len(content),
        )

    def create_directory(
        self,
        requested_path: str,
    ) -> Path:
        """Create a directory inside the allowed scope."""
        path = self._path_resolver.resolve(requested_path)

        if path.exists():
            raise FileSystemValidationError(f"Path already exists: {requested_path}")

        try:
            path.mkdir(parents=True, exist_ok=False)
        except OSError as error:
            raise FileSystemOperationError(
                f"Could not create directory: {requested_path}"
            ) from error

        logger.info(
            "Created scoped directory. path=%s",
            path,
        )

        return path

    def write_text_file(
        self,
        requested_path: str,
        content: str,
        overwrite: bool = False,
    ) -> FileWriteResult:
        """Write UTF-8 text inside the allowed scope."""
        if len(content) > self._max_write_characters:
            raise FileSystemValidationError(
                "The supplied content exceeds the configured "
                f"write limit of "
                f"{self._max_write_characters} characters."
            )

        path = self._path_resolver.resolve(requested_path)

        if path.exists() and path.is_dir():
            raise FileSystemValidationError(f"Path is a directory: {requested_path}")

        already_exists = path.exists()

        if already_exists and not overwrite:
            raise FileSystemValidationError(
                "The file already exists. Set overwrite to true to replace it."
            )

        try:
            path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
            path.write_text(
                content,
                encoding="utf-8",
            )
        except OSError as error:
            raise FileSystemOperationError(f"Could not write file: {requested_path}") from error

        logger.info(
            "Wrote scoped text file. path=%s character_count=%d overwrite=%s",
            path,
            len(content),
            already_exists,
        )

        return FileWriteResult(
            path=path,
            character_count=len(content),
            created=not already_exists,
        )

    @staticmethod
    def _build_entry(
        path: Path,
    ) -> FileSystemEntry:
        """Build metadata for one file-system entry."""
        stat_result = path.stat()

        if path.is_dir():
            entry_type = FileSystemEntryType.DIRECTORY
            size_bytes: int | None = None
        elif path.is_file():
            entry_type = FileSystemEntryType.FILE
            size_bytes = stat_result.st_size
        else:
            raise FileSystemValidationError(f"Unsupported file-system entry: {path}")

        return FileSystemEntry(
            name=path.name,
            path=path,
            entry_type=entry_type,
            size_bytes=size_bytes,
            modified_at=datetime.fromtimestamp(stat_result.st_mtime).astimezone(),
        )
