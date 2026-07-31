"""Structured logging configuration for Project ATLAS."""

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4

_REQUEST_ID: ContextVar[str] = ContextVar(
    "atlas_request_id",
    default="-",
)

SUPPORTED_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


class LoggingConfigurationError(ValueError):
    """Raised when ATLAS logging settings are invalid."""


class RequestContextFilter(logging.Filter):
    """Attach the current ATLAS request ID to each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context to a log record."""
        record.request_id = _REQUEST_ID.get()
        return True


@contextmanager
def request_context() -> Iterator[str]:
    """Create and activate a unique request ID."""
    request_id = uuid4().hex
    token = _REQUEST_ID.set(request_id)

    try:
        yield request_id
    finally:
        _REQUEST_ID.reset(token)


def get_request_id() -> str:
    """Return the currently active request ID."""
    return _REQUEST_ID.get()


def configure_logging(
    log_directory: Path,
    log_level: str = "INFO",
    max_bytes: int = 5_000_000,
    backup_count: int = 5,
) -> Path:
    """Configure console and rotating-file logging.

    Return the path of the active ATLAS log file.
    """
    normalized_level = log_level.strip().upper()

    if normalized_level not in SUPPORTED_LOG_LEVELS:
        supported = ", ".join(SUPPORTED_LOG_LEVELS)

        raise LoggingConfigurationError(
            f"Unsupported log level {log_level!r}. Supported levels are: {supported}."
        )

    if max_bytes < 1:
        raise LoggingConfigurationError("Log maximum size must be a positive integer.")

    if backup_count < 0:
        raise LoggingConfigurationError("Log backup count cannot be negative.")

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    log_file = log_directory / "atlas.log"
    numeric_level = SUPPORTED_LOG_LEVELS[normalized_level]

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)

    request_filter = RequestContextFilter()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.addFilter(request_filter)
    console_handler.setFormatter(logging.Formatter("%(levelname)s | %(name)s | %(message)s"))

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(numeric_level)
    file_handler.addFilter(request_filter)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | request=%(request_id)s | %(name)s | %(message)s"
        )
    )

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    logging.captureWarnings(True)

    logger = logging.getLogger(__name__)
    logger.info(
        "ATLAS logging initialized at %s.",
        log_file,
    )

    return log_file
