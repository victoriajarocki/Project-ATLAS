"""Tests for shared ATLAS tool-argument validation."""

import pytest

from atlas.tools.base import (
    ToolDefinition,
    ToolRiskLevel,
    ToolValidationError,
)
from atlas.tools.validation import (
    validate_tool_arguments,
)


@pytest.fixture
def definition() -> ToolDefinition:
    """Create a representative tool definition."""
    return ToolDefinition(
        name="example",
        description="Validate example arguments.",
        parameters={
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                },
                "count": {
                    "type": "integer",
                },
                "enabled": {
                    "type": "boolean",
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        risk_level=ToolRiskLevel.LOW,
        requires_confirmation=False,
    )


def test_valid_arguments_pass(
    definition: ToolDefinition,
) -> None:
    """Valid arguments should not raise an error."""
    validate_tool_arguments(
        definition=definition,
        arguments={
            "name": "ATLAS",
            "count": 3,
            "enabled": True,
        },
    )


def test_optional_arguments_may_be_omitted(
    definition: ToolDefinition,
) -> None:
    """Only required arguments should be mandatory."""
    validate_tool_arguments(
        definition=definition,
        arguments={"name": "ATLAS"},
    )


def test_missing_required_argument_fails(
    definition: ToolDefinition,
) -> None:
    """Missing required arguments should be rejected."""
    with pytest.raises(
        ToolValidationError,
        match="Missing required argument",
    ):
        validate_tool_arguments(
            definition=definition,
            arguments={},
        )


def test_unknown_argument_fails(
    definition: ToolDefinition,
) -> None:
    """Unknown arguments should be rejected."""
    with pytest.raises(
        ToolValidationError,
        match="Unknown argument",
    ):
        validate_tool_arguments(
            definition=definition,
            arguments={
                "name": "ATLAS",
                "unexpected": True,
            },
        )


def test_incorrect_string_type_fails(
    definition: ToolDefinition,
) -> None:
    """String arguments should reject other types."""
    with pytest.raises(
        ToolValidationError,
        match="must be of type string",
    ):
        validate_tool_arguments(
            definition=definition,
            arguments={"name": 123},
        )


def test_boolean_is_not_integer(
    definition: ToolDefinition,
) -> None:
    """Boolean values should not pass integer validation."""
    with pytest.raises(
        ToolValidationError,
        match="must be of type integer",
    ):
        validate_tool_arguments(
            definition=definition,
            arguments={
                "name": "ATLAS",
                "count": True,
            },
        )


def test_integer_is_not_boolean(
    definition: ToolDefinition,
) -> None:
    """Integer values should not pass boolean validation."""
    with pytest.raises(
        ToolValidationError,
        match="must be of type boolean",
    ):
        validate_tool_arguments(
            definition=definition,
            arguments={
                "name": "ATLAS",
                "enabled": 1,
            },
        )


def test_enum_rejects_unlisted_value() -> None:
    """Enum validation should reject unsupported values."""
    enum_definition = ToolDefinition(
        name="enum_example",
        description="Validate an enum.",
        parameters={
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["read", "write"],
                }
            },
            "required": ["mode"],
            "additionalProperties": False,
        },
        risk_level=ToolRiskLevel.LOW,
        requires_confirmation=False,
    )

    with pytest.raises(
        ToolValidationError,
        match="must be one of",
    ):
        validate_tool_arguments(
            definition=enum_definition,
            arguments={"mode": "delete"},
        )


def test_array_items_are_validated() -> None:
    """Array entries should use their item schema."""
    array_definition = ToolDefinition(
        name="array_example",
        description="Validate an array.",
        parameters={
            "type": "object",
            "properties": {
                "names": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                }
            },
            "required": ["names"],
            "additionalProperties": False,
        },
        risk_level=ToolRiskLevel.LOW,
        requires_confirmation=False,
    )

    with pytest.raises(
        ToolValidationError,
        match=r"names\[1\]",
    ):
        validate_tool_arguments(
            definition=array_definition,
            arguments={
                "names": ["ATLAS", 123],
            },
        )
