"""Timing utilities for measuring Project ATLAS request performance."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from time import perf_counter

from atlas.performance.models import (
    PerformanceReport,
    PerformanceStage,
    StageTiming,
)

Clock = Callable[[], float]


class PerformanceTimingError(RuntimeError):
    """Raised when a performance measurement is invalid."""


class PerformanceTracker:
    """Measure named stages and total duration for one ATLAS request."""

    def __init__(
        self,
        request_id: str | None = None,
        clock: Clock = perf_counter,
    ) -> None:
        """Initialize a request performance tracker."""
        self._request_id = request_id
        self._clock = clock
        self._started_at = self._clock()
        self._stage_timings: list[StageTiming] = []

    @property
    def request_id(self) -> str | None:
        """Return the request identifier associated with this tracker."""
        return self._request_id

    @property
    def stage_count(self) -> int:
        """Return the number of completed stage measurements."""
        return len(self._stage_timings)

    @contextmanager
    def measure(
        self,
        stage: PerformanceStage | str,
    ) -> Iterator[None]:
        """Measure one named request stage."""
        stage_name = self._normalize_stage_name(stage)
        started_at = self._clock()

        try:
            yield
        finally:
            finished_at = self._clock()
            duration_seconds = finished_at - started_at

            self.record(
                stage=stage_name,
                duration_seconds=duration_seconds,
            )

    def record(
        self,
        stage: PerformanceStage | str,
        duration_seconds: float,
    ) -> None:
        """Record a duration that was measured outside this tracker."""
        stage_name = self._normalize_stage_name(stage)

        if duration_seconds < 0:
            raise PerformanceTimingError("A performance duration cannot be negative.")

        self._stage_timings.append(
            StageTiming(
                stage=stage_name,
                duration_seconds=duration_seconds,
            )
        )

    def total_elapsed_seconds(self) -> float:
        """Return the elapsed time since this tracker was created."""
        elapsed_seconds = self._clock() - self._started_at

        if elapsed_seconds < 0:
            raise PerformanceTimingError("The performance clock moved backwards.")

        return elapsed_seconds

    def build_report(self) -> PerformanceReport:
        """Create an immutable report from the current measurements."""
        return PerformanceReport(
            request_id=self._request_id,
            stage_timings=tuple(self._stage_timings),
            total_duration_seconds=self.total_elapsed_seconds(),
        )

    @staticmethod
    def _normalize_stage_name(
        stage: PerformanceStage | str,
    ) -> str:
        """Validate and normalize a stage name."""
        stage_name = str(stage).strip()

        if not stage_name:
            raise PerformanceTimingError("A performance stage requires a non-empty name.")

        return stage_name
