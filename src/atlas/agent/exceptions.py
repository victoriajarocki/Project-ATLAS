"""Exceptions raised by the Project ATLAS agent subsystem."""


class AgentError(RuntimeError):
    """Base exception for agent operations."""


class AgentConfigurationError(AgentError):
    """Raised when agent configuration is invalid."""


class AgentDecisionError(AgentError):
    """Raised when a model produces an invalid agent decision."""


class AgentParsingError(AgentDecisionError):
    """Raised when structured model output cannot be parsed."""


class AgentStepLimitError(AgentError):
    """Raised when an agent request exceeds its step limit."""
