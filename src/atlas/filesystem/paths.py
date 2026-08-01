"""Path validation and scope enforcement for Project ATLAS."""

from pathlib import Path

from atlas.filesystem.exceptions import (
    FileSystemValidationError,
    PathOutsideAllowedScopeError,
)


class ScopedPathResolver:
    """Resolve paths while enforcing configured directory boundaries."""

    def __init__(
        self,
        allowed_directories: tuple[Path, ...],
    ) -> None:
        """Initialize the resolver with allowed root directories."""
        if not allowed_directories:
            raise FileSystemValidationError("At least one allowed directory is required.")

        resolved_directories: list[Path] = []

        for directory in allowed_directories:
            resolved = directory.expanduser().resolve()

            if not resolved.exists():
                resolved.mkdir(parents=True, exist_ok=True)

            if not resolved.is_dir():
                raise FileSystemValidationError(f"Allowed path is not a directory: {resolved}")

            resolved_directories.append(resolved)

        self._allowed_directories = tuple(resolved_directories)

    @property
    def allowed_directories(self) -> tuple[Path, ...]:
        """Return the configured allowed root directories."""
        return self._allowed_directories

    def resolve(self, requested_path: str) -> Path:
        """Resolve and validate a user-supplied path."""
        cleaned_path = requested_path.strip()

        if not cleaned_path:
            raise FileSystemValidationError("A file-system path is required.")

        candidate = Path(cleaned_path).expanduser()

        if candidate.is_absolute():
            resolved_candidate = candidate.resolve()
        else:
            resolved_candidate = (self._allowed_directories[0] / candidate).resolve()

        if not any(
            resolved_candidate == root or resolved_candidate.is_relative_to(root)
            for root in self._allowed_directories
        ):
            raise PathOutsideAllowedScopeError(
                "The requested path is outside the configured ATLAS directories."
            )

        return resolved_candidate
