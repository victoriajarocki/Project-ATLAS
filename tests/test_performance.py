"""Tests for Project ATLAS performance measurement."""

import logging
from collections.abc import Iterable

import pytest

from atlas.performance import (
    PerformanceProfiler,
    PerformanceReport,
    PerformanceStage,
    PerformanceTimingError,
    PerformanceTracker,
)


class SequenceClock:
    """Return a predefined sequence of monotonic clock values."""

    def __init__(
        self,
        values: Iterable[float],
    ) -> None:
        """Initialize the deterministic clock."""
        self._values = iter(values)

    def __call__(self) -> float:
        """Return the next configured clock value."""
        return next(self._values)


def test_tracker_records_measured_stage() -> None:
    """A measured context should create one stage timing."""
    clock = SequenceClock([10.0, 11.0, 13.5, 14.0])
    tracker = PerformanceTracker(
        request_id="request-1",
        clock=clock,
    )

    with tracker.measure(PerformanceStage.PROVIDER_REQUEST):
        pass

    report = tracker.build_report()

    assert report.request_id == "request-1"
    assert report.stage_count == 1
    assert report.stage_timings[0].stage == "provider_request"
    assert report.stage_timings[0].duration_seconds == 2.5
    assert report.total_duration_seconds == 4.0


def test_tracker_records_external_duration() -> None:
    """A caller should be able to record an existing measurement."""
    clock = SequenceClock([5.0, 8.0])
    tracker = PerformanceTracker(clock=clock)

    tracker.record(
        stage=PerformanceStage.TOOL_EXECUTION,
        duration_seconds=0.25,
    )

    report = tracker.build_report()

    assert report.stage_count == 1
    assert report.duration_for(PerformanceStage.TOOL_EXECUTION) == 0.25
    assert report.total_duration_seconds == 3.0


def test_report_combines_repeated_stage_durations() -> None:
    """Repeated measurements should be combined by duration_for."""
    clock = SequenceClock([1.0, 2.0])
    tracker = PerformanceTracker(clock=clock)

    tracker.record("provider_request", 1.5)
    tracker.record("provider_request", 2.0)

    report = tracker.build_report()

    assert report.stage_count == 2
    assert report.duration_for("provider_request") == 3.5


def test_measure_records_stage_when_operation_raises() -> None:
    """A failed operation should still have its duration recorded."""
    clock = SequenceClock([10.0, 11.0, 12.0, 13.0])
    tracker = PerformanceTracker(clock=clock)

    with pytest.raises(ValueError, match="failed"):
        with tracker.measure(PerformanceStage.TOOL_EXECUTION):
            raise ValueError("failed")

    report = tracker.build_report()

    assert report.stage_count == 1
    assert report.duration_for(PerformanceStage.TOOL_EXECUTION) == 1.0
    assert report.total_duration_seconds == 3.0


def test_empty_stage_name_is_rejected() -> None:
    """A stage name must contain non-whitespace text."""
    clock = SequenceClock([1.0])
    tracker = PerformanceTracker(clock=clock)

    with pytest.raises(
        PerformanceTimingError,
        match="non-empty name",
    ):
        tracker.record(
            stage="   ",
            duration_seconds=1.0,
        )


def test_negative_duration_is_rejected() -> None:
    """Recorded durations must not be negative."""
    clock = SequenceClock([1.0])
    tracker = PerformanceTracker(clock=clock)

    with pytest.raises(
        PerformanceTimingError,
        match="cannot be negative",
    ):
        tracker.record(
            stage=PerformanceStage.MEMORY_RETRIEVAL,
            duration_seconds=-0.1,
        )


def test_clock_moving_backwards_is_rejected() -> None:
    """A non-monotonic clock should fail safely."""
    clock = SequenceClock([10.0, 9.0])
    tracker = PerformanceTracker(clock=clock)

    with pytest.raises(
        PerformanceTimingError,
        match="moved backwards",
    ):
        tracker.total_elapsed_seconds()


def test_stage_count_updates_after_measurement() -> None:
    """The tracker should expose its current number of measurements."""
    clock = SequenceClock([1.0, 2.0, 3.0])
    tracker = PerformanceTracker(clock=clock)

    assert tracker.stage_count == 0

    with tracker.measure(PerformanceStage.COMMAND_DETECTION):
        pass

    assert tracker.stage_count == 1


def test_profiler_measures_stage_and_finishes() -> None:
    """The profiler should measure stages and produce a report."""
    clock = SequenceClock([10.0, 11.0, 13.0, 15.0])
    profiler = PerformanceProfiler(
        request_id="request-2",
        clock=clock,
    )

    with profiler.stage(PerformanceStage.PROVIDER_REQUEST):
        pass

    report = profiler.finish()

    assert report.request_id == "request-2"
    assert report.stage_count == 1
    assert report.duration_for(PerformanceStage.PROVIDER_REQUEST) == 2.0
    assert report.total_duration_seconds == 5.0
    assert profiler.finished is True


def test_profiler_can_record_external_duration() -> None:
    """The profiler should accept externally measured durations."""
    clock = SequenceClock([4.0, 6.0])
    profiler = PerformanceProfiler(clock=clock)

    profiler.record(
        PerformanceStage.TOOL_EXECUTION,
        0.75,
    )

    report = profiler.finish()

    assert report.duration_for(PerformanceStage.TOOL_EXECUTION) == 0.75
    assert report.total_duration_seconds == 2.0


def test_profiler_finish_is_idempotent() -> None:
    """Finishing repeatedly should return the same report."""
    clock = SequenceClock([1.0, 2.0])
    profiler = PerformanceProfiler(clock=clock)

    first_report = profiler.finish()
    second_report = profiler.finish()

    assert first_report is second_report


def test_profiler_report_finishes_profiler() -> None:
    """Requesting a report should finalize the profiler."""
    clock = SequenceClock([2.0, 4.0])
    profiler = PerformanceProfiler(clock=clock)

    report = profiler.report()

    assert isinstance(report, PerformanceReport)
    assert profiler.finished is True
    assert report.total_duration_seconds == 2.0


def test_profiler_publishes_report_to_consumer() -> None:
    """The final report should be delivered to the configured consumer."""
    reports: list[PerformanceReport] = []
    clock = SequenceClock([3.0, 5.0])
    profiler = PerformanceProfiler(
        request_id="consumer-request",
        clock=clock,
        report_consumer=reports.append,
    )

    report = profiler.finish()

    assert reports == [report]


def test_profiler_consumer_runs_only_once() -> None:
    """Repeated finish calls should not publish duplicate reports."""
    reports: list[PerformanceReport] = []
    clock = SequenceClock([1.0, 2.0])
    profiler = PerformanceProfiler(
        clock=clock,
        report_consumer=reports.append,
    )

    profiler.finish()
    profiler.finish()

    assert len(reports) == 1


def test_finished_profiler_rejects_new_stage() -> None:
    """A finished profiler must not accept new measurements."""
    clock = SequenceClock([1.0, 2.0])
    profiler = PerformanceProfiler(clock=clock)
    profiler.finish()

    with pytest.raises(
        RuntimeError,
        match="cannot record additional stages",
    ):
        with profiler.stage(PerformanceStage.TOOL_EXECUTION):
            pass


def test_finished_profiler_rejects_external_record() -> None:
    """A finished profiler must not accept external measurements."""
    clock = SequenceClock([1.0, 2.0])
    profiler = PerformanceProfiler(clock=clock)
    profiler.finish()

    with pytest.raises(
        RuntimeError,
        match="cannot record additional stages",
    ):
        profiler.record(
            PerformanceStage.TOOL_EXECUTION,
            0.5,
        )


def test_profiler_records_failed_stage() -> None:
    """A failing stage should still appear in the final report."""
    clock = SequenceClock([10.0, 11.0, 12.0, 13.0])
    profiler = PerformanceProfiler(clock=clock)

    with pytest.raises(ValueError, match="failure"):
        with profiler.stage(PerformanceStage.PROVIDER_REQUEST):
            raise ValueError("failure")

    report = profiler.finish()

    assert report.stage_count == 1
    assert report.duration_for(PerformanceStage.PROVIDER_REQUEST) == 1.0
    assert report.total_duration_seconds == 3.0


def test_profiler_logs_summary_and_stage(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Finishing should log the report summary and stage measurements."""
    clock = SequenceClock([10.0, 11.0, 12.0, 13.0])
    profiler = PerformanceProfiler(
        request_id="logged-request",
        clock=clock,
    )

    with caplog.at_level(
        logging.INFO,
        logger="atlas.performance.profiler",
    ):
        with profiler.stage(PerformanceStage.PROMPT_CONSTRUCTION):
            pass

        profiler.finish()

    assert "Performance report completed." in caplog.text
    assert "request_id=logged-request" in caplog.text
    assert "stage=prompt_construction" in caplog.text
    assert "duration=1.000000" in caplog.text
