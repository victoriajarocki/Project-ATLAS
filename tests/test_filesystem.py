"""Tests for the scoped ATLAS file-system subsystem."""

from pathlib import Path

import pytest

from atlas.filesystem.exceptions import (
    FileSystemValidationError,
    PathOutsideAllowedScopeError,
)
from atlas.filesystem.models import FileSystemEntryType
from atlas.filesystem.paths import ScopedPathResolver
from atlas.filesystem.service import FileSystemService


@pytest.fixture
def allowed_directory(
    tmp_path: Path,
) -> Path:
    """Create an isolated directory that ATLAS may access."""
    directory = tmp_path / "workspace"
    directory.mkdir()

    return directory


@pytest.fixture
def resolver(
    allowed_directory: Path,
) -> ScopedPathResolver:
    """Create a scoped path resolver for the test workspace."""
    return ScopedPathResolver(allowed_directories=(allowed_directory,))


@pytest.fixture
def filesystem_service(
    resolver: ScopedPathResolver,
) -> FileSystemService:
    """Create a file-system service with small test limits."""
    return FileSystemService(
        path_resolver=resolver,
        max_read_bytes=1_000,
        max_write_characters=1_000,
    )


def test_resolver_requires_allowed_directory() -> None:
    """The resolver should require at least one allowed root."""
    with pytest.raises(FileSystemValidationError):
        ScopedPathResolver(allowed_directories=())


def test_resolver_creates_missing_allowed_directory(
    tmp_path: Path,
) -> None:
    """A missing configured root should be created."""
    directory = tmp_path / "new_workspace"

    scoped_resolver = ScopedPathResolver(allowed_directories=(directory,))

    assert directory.exists()
    assert directory.is_dir()
    assert scoped_resolver.allowed_directories == (directory.resolve(),)


def test_resolver_rejects_allowed_path_that_is_file(
    tmp_path: Path,
) -> None:
    """Configured roots must be directories."""
    file_path = tmp_path / "not_a_directory.txt"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(FileSystemValidationError):
        ScopedPathResolver(allowed_directories=(file_path,))


def test_resolver_resolves_relative_path_inside_scope(
    resolver: ScopedPathResolver,
    allowed_directory: Path,
) -> None:
    """Relative paths should resolve inside the first root."""
    resolved = resolver.resolve("notes/example.txt")

    assert resolved == (allowed_directory / "notes" / "example.txt").resolve()


def test_resolver_allows_root_directory(
    resolver: ScopedPathResolver,
    allowed_directory: Path,
) -> None:
    """The allowed root itself should be accessible."""
    resolved = resolver.resolve(".")

    assert resolved == allowed_directory.resolve()


def test_resolver_rejects_empty_path(
    resolver: ScopedPathResolver,
) -> None:
    """Empty file-system paths should be rejected."""
    with pytest.raises(FileSystemValidationError):
        resolver.resolve("   ")


def test_resolver_rejects_relative_scope_escape(
    resolver: ScopedPathResolver,
) -> None:
    """Parent traversal outside the allowed root should fail."""
    with pytest.raises(PathOutsideAllowedScopeError):
        resolver.resolve("../outside.txt")


def test_resolver_rejects_absolute_path_outside_scope(
    resolver: ScopedPathResolver,
    tmp_path: Path,
) -> None:
    """Absolute paths outside the root should be rejected."""
    outside_path = tmp_path / "outside.txt"

    with pytest.raises(PathOutsideAllowedScopeError):
        resolver.resolve(str(outside_path))


def test_resolver_accepts_absolute_path_inside_scope(
    resolver: ScopedPathResolver,
    allowed_directory: Path,
) -> None:
    """Absolute paths inside the allowed root should work."""
    target = allowed_directory / "inside.txt"

    resolved = resolver.resolve(str(target))

    assert resolved == target.resolve()


def test_list_directory_returns_sorted_entries(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Directories should appear before files and sort by name."""
    (allowed_directory / "Zulu.txt").write_text(
        "z",
        encoding="utf-8",
    )
    (allowed_directory / "alpha.txt").write_text(
        "a",
        encoding="utf-8",
    )
    (allowed_directory / "Bravo").mkdir()
    (allowed_directory / "alpha_folder").mkdir()

    entries = filesystem_service.list_directory(".")

    assert [entry.name for entry in entries] == [
        "alpha_folder",
        "Bravo",
        "alpha.txt",
        "Zulu.txt",
    ]


def test_list_directory_reports_entry_types(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Directory listings should identify files and folders."""
    directory = allowed_directory / "documents"
    directory.mkdir()

    file_path = allowed_directory / "notes.txt"
    file_path.write_text("hello", encoding="utf-8")

    entries = filesystem_service.list_directory(".")
    entries_by_name = {entry.name: entry for entry in entries}

    assert entries_by_name["documents"].entry_type is FileSystemEntryType.DIRECTORY
    assert entries_by_name["documents"].size_bytes is None

    assert entries_by_name["notes.txt"].entry_type is FileSystemEntryType.FILE
    assert entries_by_name["notes.txt"].size_bytes == 5


def test_list_directory_rejects_missing_directory(
    filesystem_service: FileSystemService,
) -> None:
    """Missing directories should produce validation errors."""
    with pytest.raises(FileSystemValidationError):
        filesystem_service.list_directory("missing")


def test_list_directory_rejects_file_path(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """A file cannot be listed as a directory."""
    (allowed_directory / "notes.txt").write_text(
        "hello",
        encoding="utf-8",
    )

    with pytest.raises(FileSystemValidationError):
        filesystem_service.list_directory("notes.txt")


def test_get_info_returns_file_metadata(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """File metadata should contain type and size."""
    file_path = allowed_directory / "rocket.txt"
    file_path.write_text("Wraith", encoding="utf-8")

    entry = filesystem_service.get_info("rocket.txt")

    assert entry.name == "rocket.txt"
    assert entry.entry_type is FileSystemEntryType.FILE
    assert entry.size_bytes == 6
    assert entry.modified_at.tzinfo is not None


def test_get_info_returns_directory_metadata(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Directory metadata should not report a file size."""
    (allowed_directory / "designs").mkdir()

    entry = filesystem_service.get_info("designs")

    assert entry.name == "designs"
    assert entry.entry_type is FileSystemEntryType.DIRECTORY
    assert entry.size_bytes is None


def test_get_info_rejects_missing_path(
    filesystem_service: FileSystemService,
) -> None:
    """Missing metadata targets should be rejected."""
    with pytest.raises(FileSystemValidationError):
        filesystem_service.get_info("missing.txt")


def test_read_text_file_returns_content(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """UTF-8 text files should be readable."""
    file_path = allowed_directory / "notes.txt"
    file_path.write_text(
        "Project ATLAS",
        encoding="utf-8",
    )

    result = filesystem_service.read_text_file("notes.txt")

    assert result.path == file_path.resolve()
    assert result.content == "Project ATLAS"
    assert result.character_count == 13


def test_read_text_file_rejects_missing_file(
    filesystem_service: FileSystemService,
) -> None:
    """Missing files should be rejected."""
    with pytest.raises(FileSystemValidationError):
        filesystem_service.read_text_file("missing.txt")


def test_read_text_file_rejects_directory(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Directories cannot be read as text files."""
    (allowed_directory / "documents").mkdir()

    with pytest.raises(FileSystemValidationError):
        filesystem_service.read_text_file("documents")


def test_read_text_file_rejects_oversized_file(
    resolver: ScopedPathResolver,
    allowed_directory: Path,
) -> None:
    """Files larger than the configured limit should fail."""
    service = FileSystemService(
        path_resolver=resolver,
        max_read_bytes=5,
        max_write_characters=1_000,
    )

    (allowed_directory / "large.txt").write_text(
        "123456",
        encoding="utf-8",
    )

    with pytest.raises(FileSystemValidationError):
        service.read_text_file("large.txt")


def test_read_text_file_rejects_invalid_utf8(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Binary or invalid UTF-8 content should be rejected."""
    file_path = allowed_directory / "binary.bin"
    file_path.write_bytes(b"\xff\xfe\xfd")

    with pytest.raises(FileSystemValidationError):
        filesystem_service.read_text_file("binary.bin")


def test_create_directory_creates_nested_path(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Nested directories should be created inside scope."""
    created_path = filesystem_service.create_directory("rockets/wraith")

    assert created_path == (allowed_directory / "rockets" / "wraith").resolve()
    assert created_path.is_dir()


def test_create_directory_rejects_existing_path(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Existing paths should not be recreated."""
    (allowed_directory / "existing").mkdir()

    with pytest.raises(FileSystemValidationError):
        filesystem_service.create_directory("existing")


def test_write_text_file_creates_file(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Text writing should create a new UTF-8 file."""
    result = filesystem_service.write_text_file(
        requested_path="notes/rocket.txt",
        content="Wraith",
    )

    expected_path = (allowed_directory / "notes" / "rocket.txt").resolve()

    assert result.path == expected_path
    assert result.character_count == 6
    assert result.created is True
    assert expected_path.read_text(encoding="utf-8") == "Wraith"


def test_write_text_file_rejects_existing_file_without_overwrite(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Existing files should be protected by default."""
    file_path = allowed_directory / "notes.txt"
    file_path.write_text("old", encoding="utf-8")

    with pytest.raises(FileSystemValidationError):
        filesystem_service.write_text_file(
            requested_path="notes.txt",
            content="new",
        )

    assert file_path.read_text(encoding="utf-8") == "old"


def test_write_text_file_overwrites_when_explicitly_allowed(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Explicit overwrite should replace an existing file."""
    file_path = allowed_directory / "notes.txt"
    file_path.write_text("old", encoding="utf-8")

    result = filesystem_service.write_text_file(
        requested_path="notes.txt",
        content="new",
        overwrite=True,
    )

    assert result.created is False
    assert result.character_count == 3
    assert file_path.read_text(encoding="utf-8") == "new"


def test_write_text_file_rejects_directory_target(
    filesystem_service: FileSystemService,
    allowed_directory: Path,
) -> None:
    """Directories cannot be overwritten as text files."""
    (allowed_directory / "documents").mkdir()

    with pytest.raises(FileSystemValidationError):
        filesystem_service.write_text_file(
            requested_path="documents",
            content="invalid",
            overwrite=True,
        )


def test_write_text_file_rejects_oversized_content(
    resolver: ScopedPathResolver,
) -> None:
    """Content larger than the write limit should fail."""
    service = FileSystemService(
        path_resolver=resolver,
        max_read_bytes=1_000,
        max_write_characters=5,
    )

    with pytest.raises(FileSystemValidationError):
        service.write_text_file(
            requested_path="large.txt",
            content="123456",
        )


def test_service_rejects_invalid_read_limit(
    resolver: ScopedPathResolver,
) -> None:
    """Read limits must be positive."""
    with pytest.raises(FileSystemValidationError):
        FileSystemService(
            path_resolver=resolver,
            max_read_bytes=0,
        )


def test_service_rejects_invalid_write_limit(
    resolver: ScopedPathResolver,
) -> None:
    """Write limits must be positive."""
    with pytest.raises(FileSystemValidationError):
        FileSystemService(
            path_resolver=resolver,
            max_write_characters=0,
        )
