"""Shared argument validation for Project ATLAS tools."""

from typing import Any

from atlas.tools.base import (
    ToolDefinition,
    ToolValidationError,
)


def validate_tool_arguments(
    definition: ToolDefinition,
    arguments: dict[str, Any],
) -> None:
    """Validate tool arguments against its parameter schema."""
    schema = definition.parameters

    if not isinstance(schema, dict):
        raise ToolValidationError(f"Tool {definition.name!r} has an invalid parameter schema.")

    schema_type = schema.get("type")

    if schema_type != "object":
        raise ToolValidationError(
            f"Tool {definition.name!r} must define an object parameter schema."
        )

    properties_value = schema.get("properties", {})

    if not isinstance(properties_value, dict):
        raise ToolValidationError(f"Tool {definition.name!r} has invalid schema properties.")

    required_value = schema.get("required", [])

    if not isinstance(required_value, list) or not all(
        isinstance(item, str) for item in required_value
    ):
        raise ToolValidationError(
            f"Tool {definition.name!r} has an invalid required-arguments schema."
        )

    missing_arguments = [
        argument_name for argument_name in required_value if argument_name not in arguments
    ]

    if missing_arguments:
        formatted_names = ", ".join(sorted(missing_arguments))

        raise ToolValidationError(f"Missing required argument(s): {formatted_names}.")

    additional_properties = schema.get(
        "additionalProperties",
        True,
    )

    if additional_properties is False:
        unknown_arguments = sorted(set(arguments) - set(properties_value))

        if unknown_arguments:
            formatted_names = ", ".join(unknown_arguments)

            raise ToolValidationError(f"Unknown argument(s): {formatted_names}.")

    for argument_name, argument_value in arguments.items():
        property_schema = properties_value.get(argument_name)

        if property_schema is None:
            continue

        if not isinstance(property_schema, dict):
            raise ToolValidationError(
                f"Tool {definition.name!r} has an invalid schema for argument {argument_name!r}."
            )

        _validate_value(
            value=argument_value,
            schema=property_schema,
            path=argument_name,
        )


def _validate_value(
    value: Any,
    schema: dict[str, Any],
    path: str,
) -> None:
    """Validate one value against a supported JSON schema."""
    expected_type = schema.get("type")

    if expected_type is not None:
        _validate_type(
            value=value,
            expected_type=expected_type,
            path=path,
        )

    enum_values = schema.get("enum")

    if enum_values is not None:
        if not isinstance(enum_values, list):
            raise ToolValidationError(f"Invalid enum schema for {path!r}.")

        if value not in enum_values:
            allowed_values = ", ".join(repr(item) for item in enum_values)

            raise ToolValidationError(f"Argument {path!r} must be one of: {allowed_values}.")

    if expected_type == "object":
        _validate_object(
            value=value,
            schema=schema,
            path=path,
        )

    if expected_type == "array":
        _validate_array(
            value=value,
            schema=schema,
            path=path,
        )


def _validate_type(
    value: Any,
    expected_type: Any,
    path: str,
) -> None:
    """Validate the basic JSON type of one value."""
    if not isinstance(expected_type, str):
        raise ToolValidationError(f"Invalid type schema for {path!r}.")

    valid = False

    if expected_type == "string":
        valid = isinstance(value, str)

    elif expected_type == "boolean":
        valid = isinstance(value, bool)

    elif expected_type == "integer":
        valid = isinstance(value, int) and not isinstance(value, bool)

    elif expected_type == "number":
        valid = isinstance(value, (int, float)) and not isinstance(value, bool)

    elif expected_type == "object":
        valid = isinstance(value, dict)

    elif expected_type == "array":
        valid = isinstance(value, list)

    elif expected_type == "null":
        valid = value is None

    else:
        raise ToolValidationError(f"Unsupported schema type {expected_type!r} for {path!r}.")

    if not valid:
        raise ToolValidationError(f"Argument {path!r} must be of type {expected_type}.")


def _validate_object(
    value: Any,
    schema: dict[str, Any],
    path: str,
) -> None:
    """Validate a nested object."""
    if not isinstance(value, dict):
        return

    properties_value = schema.get(
        "properties",
        {},
    )

    if not isinstance(properties_value, dict):
        raise ToolValidationError(f"Invalid object schema for {path!r}.")

    required_value = schema.get("required", [])

    if not isinstance(required_value, list) or not all(
        isinstance(item, str) for item in required_value
    ):
        raise ToolValidationError(f"Invalid required schema for {path!r}.")

    missing_arguments = [
        argument_name for argument_name in required_value if argument_name not in value
    ]

    if missing_arguments:
        formatted_names = ", ".join(sorted(missing_arguments))

        raise ToolValidationError(f"Missing required argument(s) in {path!r}: {formatted_names}.")

    if schema.get("additionalProperties", True) is False:
        unknown_arguments = sorted(set(value) - set(properties_value))

        if unknown_arguments:
            formatted_names = ", ".join(unknown_arguments)

            raise ToolValidationError(f"Unknown argument(s) in {path!r}: {formatted_names}.")

    for child_name, child_value in value.items():
        child_schema = properties_value.get(child_name)

        if child_schema is None:
            continue

        if not isinstance(child_schema, dict):
            raise ToolValidationError(f"Invalid schema for {path}.{child_name}.")

        _validate_value(
            value=child_value,
            schema=child_schema,
            path=f"{path}.{child_name}",
        )


def _validate_array(
    value: Any,
    schema: dict[str, Any],
    path: str,
) -> None:
    """Validate items inside an array."""
    if not isinstance(value, list):
        return

    item_schema = schema.get("items")

    if item_schema is None:
        return

    if not isinstance(item_schema, dict):
        raise ToolValidationError(f"Invalid item schema for {path!r}.")

    for index, item in enumerate(value):
        _validate_value(
            value=item,
            schema=item_schema,
            path=f"{path}[{index}]",
        )
