"""Performance profiling coordination for Project ATLAS."""

import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from time import perf_counter

from atlas.performance.models import (
    PerformanceReport,
    PerformanceStage,
)
from atlas.performance.timing import (
    Clock,
    PerformanceTracker,
)

logger = logging.getLogger(__name__)

ReportConsumer = Callable[[PerformanceReport], None]


class PerformanceProfiler:
    """Coordinate request-stage timing and performance reporting."""

    def __init__(
        self,
        request_id: str | None = None,
        clock: Clock = perf_counter,
        report_consumer: ReportConsumer | None = None,
    ) -> None:
        """Initialize a profiler for one ATLAS operation."""
        self._tracker = PerformanceTracker(
            request_id=request_id,
            clock=clock,
        )
        self._report_consumer = report_consumer
        self._finished_report: PerformanceReport | None = None

    @property
    def request_id(self) -> str | None:
        """Return the request identifier associated with the profiler."""
        return self._tracker.request_id

    @property
    def stage_count(self) -> int:
        """Return the number of completed stage measurements."""
        return self._tracker.stage_count

    @property
    def finished(self) -> bool:
        """Report whether the profiler has produced its final report."""
        return self._finished_report is not None

    @contextmanager
    def stage(
        self,
        stage: PerformanceStage | str,
    ) -> Iterator[None]:
        """Measure one named performance stage."""
        if self.finished:
            raise RuntimeError("A finished performance profiler cannot record additional stages.")

        with self._tracker.measure(stage):
            yield

    def record(
        self,
        stage: PerformanceStage | str,
        duration_seconds: float,
    ) -> None:
        """Record a duration measured by another component."""
        if self.finished:
            raise RuntimeError("A finished performance profiler cannot record additional stages.")

        self._tracker.record(
            stage=stage,
            duration_seconds=duration_seconds,
        )

    def finish(self) -> PerformanceReport:
        """Finalize, publish, and return the performance report."""
        if self._finished_report is not None:
            return self._finished_report

        report = self._tracker.build_report()
        self._finished_report = report

        self._log_report(report)

        if self._report_consumer is not None:
            self._report_consumer(report)

        return report

    def report(self) -> PerformanceReport:
        """Return the final report, finishing the profiler if necessary."""
        return self.finish()

    @staticmethod
    def _log_report(
        report: PerformanceReport,
    ) -> None:
        """Write a structured performance summary to the application log."""
        logger.info(
            "Performance report completed. request_id=%s stage_count=%d total_duration=%.6f",
            report.request_id,
            report.stage_count,
            report.total_duration_seconds,
        )

        for timing in report.stage_timings:
            logger.info(
                "Performance stage completed. request_id=%s stage=%s duration=%.6f",
                report.request_id,
                timing.stage,
                timing.duration_seconds,
            )
