"""Tests for ATLAS structured logging."""

import logging
from pathlib import Path

import pytest

from atlas.observability.logging import (
    LoggingConfigurationError,
    configure_logging,
    get_request_id,
    request_context,
)


def test_configure_logging_creates_log_file(
    tmp_path: Path,
) -> None:
    """Logging configuration should create the ATLAS log."""
    log_file = configure_logging(
        log_directory=tmp_path,
        log_level="INFO",
        max_bytes=10_000,
        backup_count=2,
    )

    logger = logging.getLogger("atlas.test")
    logger.info("Observability test message.")

    for handler in logging.getLogger().handlers:
        handler.flush()

    assert log_file.exists()

    content = log_file.read_text(encoding="utf-8")

    assert "Observability test message." in content
    assert "request=-" in content


def test_request_context_assigns_request_id() -> None:
    """A request context should provide a unique ID."""
    assert get_request_id() == "-"

    with request_context() as request_id:
        assert request_id != "-"
        assert get_request_id() == request_id

    assert get_request_id() == "-"


def test_request_id_is_written_to_log(
    tmp_path: Path,
) -> None:
    """Log entries should include their request ID."""
    log_file = configure_logging(
        log_directory=tmp_path,
        log_level="INFO",
        max_bytes=10_000,
        backup_count=1,
    )

    logger = logging.getLogger("atlas.request-test")

    with request_context() as request_id:
        logger.info("Request-scoped log message.")

    for handler in logging.getLogger().handlers:
        handler.flush()

    content = log_file.read_text(encoding="utf-8")

    assert f"request={request_id}" in content
    assert "Request-scoped log message." in content


def test_invalid_log_level_is_rejected(
    tmp_path: Path,
) -> None:
    """Unknown log levels should be rejected."""
    with pytest.raises(LoggingConfigurationError):
        configure_logging(
            log_directory=tmp_path,
            log_level="LOUD",
        )


def test_invalid_rotation_size_is_rejected(
    tmp_path: Path,
) -> None:
    """Non-positive log sizes should be rejected."""
    with pytest.raises(LoggingConfigurationError):
        configure_logging(
            log_directory=tmp_path,
            max_bytes=0,
        )


def test_negative_backup_count_is_rejected(
    tmp_path: Path,
) -> None:
    """Negative backup counts should be rejected."""
    with pytest.raises(LoggingConfigurationError):
        configure_logging(
            log_directory=tmp_path,
            backup_count=-1,
        )
