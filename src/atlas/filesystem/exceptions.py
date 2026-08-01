"""Exceptions raised by the ATLAS file-system subsystem."""


class FileSystemError(RuntimeError):
    """Base exception for file-system operations."""


class FileSystemValidationError(FileSystemError):
    """Raised when a file-system request is invalid."""


class PathOutsideAllowedScopeError(FileSystemValidationError):
    """Raised when a path escapes the configured allowed directories."""


class FileSystemOperationError(FileSystemError):
    """Raised when an authorized file-system operation fails."""
