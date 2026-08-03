"""Data models for measuring Project ATLAS performance."""

from dataclasses import dataclass
from enum import StrEnum


class PerformanceStage(StrEnum):
    """Identify a measurable stage in the ATLAS request pipeline."""

    INPUT_CLEANING = "input_cleaning"
    COMMAND_DETECTION = "command_detection"
    MEMORY_RETRIEVAL = "memory_retrieval"
    CONVERSATION_RETRIEVAL = "conversation_retrieval"
    CONTEXT_CONSTRUCTION = "context_construction"
    DETERMINISTIC_ROUTING = "deterministic_routing"
    PROMPT_CONSTRUCTION = "prompt_construction"
    PROVIDER_REQUEST = "provider_request"
    DECISION_PARSING = "decision_parsing"
    TOOL_LOOKUP = "tool_lookup"
    ARGUMENT_VALIDATION = "argument_validation"
    PERMISSION_EVALUATION = "permission_evaluation"
    TOOL_EXECUTION = "tool_execution"
    CONVERSATION_STORAGE = "conversation_storage"


@dataclass(frozen=True)
class StageTiming:
    """Represent the measured duration of one request stage."""

    stage: str
    duration_seconds: float


@dataclass(frozen=True)
class PerformanceReport:
    """Represent all performance measurements for one request."""

    request_id: str | None
    stage_timings: tuple[StageTiming, ...]
    total_duration_seconds: float

    @property
    def stage_count(self) -> int:
        """Return the number of recorded stage measurements."""
        return len(self.stage_timings)

    def duration_for(
        self,
        stage: PerformanceStage | str,
    ) -> float:
        """Return the combined duration recorded for a stage."""
        stage_name = str(stage)

        return sum(
            timing.duration_seconds for timing in self.stage_timings if timing.stage == stage_name
        )
