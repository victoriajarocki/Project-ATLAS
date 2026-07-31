# Project ATLAS Tool System

The ATLAS tool system provides a controlled and extensible mechanism for performing actions.

Tools are separate from model providers. A model generates language; a tool performs a defined operation.

---

## Current Architecture

```text
User request
    ↓
ATLAS Core
    ↓
Tool Registry
    ↓
Tool Executor
    ↓
Registered Tool
    ↓
Tool Result
```

Only registered tools can be executed.

---

## Current Tools

ATLAS v0.7.0 includes two built-in low-risk tools:

- `calculator`
- `current_time`

List registered tools from the ATLAS CLI:

```text
tools
```

---

## Calculator

The calculator evaluates restricted arithmetic expressions.

Example:

```text
tool calculator {"expression": "(12 + 8) * 4"}
```

Expected response:

```text
Tool calculator result: 80
```

Supported operations include:

- Addition
- Subtraction
- Multiplication
- Division
- Floor division
- Modulo
- Powers
- Parentheses
- Positive and negative numeric values

The calculator does not use Python's `eval()`.

It rejects:

- Imports
- Function calls
- Attribute access
- Variables
- Strings
- Boolean values
- Unsupported syntax
- Excessively large exponents

Unsafe example:

```text
tool calculator {"expression": "__import__('os')"}
```

The expression should be rejected.

---

## Current Time

The current-time tool returns the local date and time of the computer running ATLAS.

Example:

```text
tool current_time {}
```

The tool accepts no arguments.

---

## Tool Interface

Every ATLAS tool implements the abstract `Tool` interface.

A tool must expose:

```python
@property
def definition(self) -> ToolDefinition:
    """Return the tool definition."""
```

and:

```python
def execute(
    self,
    arguments: dict[str, Any],
) -> ToolResult:
    """Execute the tool."""
```

---

## Tool Definition

A `ToolDefinition` contains:

- `name`
- `description`
- `parameters`
- `risk_level`
- `requires_confirmation`

Example:

```python
ToolDefinition(
    name="calculator",
    description="Evaluate a basic arithmetic expression.",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
            }
        },
        "required": ["expression"],
        "additionalProperties": False,
    },
    risk_level=ToolRiskLevel.LOW,
    requires_confirmation=False,
)
```

Tool names should be:

- Unique
- Lowercase
- Descriptive
- Stable across releases

---

## Tool Risk Levels

ATLAS defines three tool-risk levels:

```text
low
medium
high
```

### Low Risk

Examples:

- Arithmetic calculation
- Reading the local time
- Reading public information

These generally do not modify user data or control external systems.

### Medium Risk

Future examples:

- Creating a file
- Renaming a file
- Opening an application
- Sending a notification

These may modify state and should normally require permission or confirmation.

### High Risk

Future examples:

- Deleting files
- Running unrestricted terminal commands
- Sending email
- Controlling physical hardware
- Modifying system settings

These require strict controls, clear approval, and detailed auditing.

The permission system is planned for ATLAS v0.8.0.

---

## Tool Registry

`ToolRegistry` stores available tool implementations.

Register a tool:

```python
registry = ToolRegistry()
registry.register(CalculatorTool())
```

Retrieve a tool:

```python
tool = registry.get("calculator")
```

List definitions:

```python
definitions = registry.list_definitions()
```

Duplicate names are rejected.

Unknown tool names produce `ToolNotFoundError`.

---

## Tool Executor

`ToolExecutor` is the controlled entry point for execution.

Example:

```python
result = executor.execute(
    tool_name="calculator",
    arguments={"expression": "2 + 2"},
)
```

The executor:

- Retrieves the registered tool
- Records execution timing
- Logs the tool name and risk level
- Executes the tool
- Returns a structured result
- Converts unexpected failures into tool-system errors

Tool arguments should not be written to logs when they may contain sensitive information.

---

## Tool Results

A successful result resembles:

```python
ToolResult(
    tool_name="calculator",
    success=True,
    output="4",
)
```

A `ToolResult` contains:

- Tool name
- Success status
- Output
- Optional error message

---

## Tool Exceptions

The tool system defines:

```text
ToolError
ToolValidationError
ToolExecutionError
ToolNotFoundError
```

### `ToolValidationError`

Used when arguments are missing, malformed, unsupported, or unsafe.

### `ToolExecutionError`

Used when the tool cannot complete the operation.

### `ToolNotFoundError`

Used when the requested tool is not registered.

---

## Creating a New Tool

Create a module inside:

```text
src/atlas/tools/builtin/
```

Example:

```text
src/atlas/tools/builtin/example.py
```

Implement the interface:

```python
"""Example ATLAS tool."""

from typing import Any

from atlas.tools.base import (
    Tool,
    ToolDefinition,
    ToolResult,
    ToolRiskLevel,
)


class ExampleTool(Tool):
    """Demonstrate the ATLAS tool interface."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the example-tool definition."""
        return ToolDefinition(
            name="example",
            description="Return an example result.",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute the example tool."""
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output="Example result.",
        )
```

Export it from:

```text
src/atlas/tools/builtin/__init__.py
```

Register it during application startup:

```python
tool_registry.register(ExampleTool())
```

Add tests before considering the tool complete.

---

## Tool Test Requirements

Every tool should test:

- Registration
- Valid input
- Missing arguments
- Incorrect argument types
- Unsupported arguments
- Boundary values
- Failure behavior
- Security-sensitive input
- Correct risk metadata

Run tool tests:

```powershell
pytest tests\test_tools.py
```

Run the entire suite:

```powershell
pytest
```

---

## Security Requirements

A tool must never assume model output is safe.

Every tool must:

1. Validate all arguments.
2. Reject unknown parameters when appropriate.
3. Enforce resource limits.
4. Avoid unrestricted code evaluation.
5. Use the lowest practical level of access.
6. Return controlled errors.
7. Assign an accurate risk level.
8. Require confirmation when an action can affect user data or external systems.
9. Avoid logging sensitive arguments.
10. Include security-focused tests.

---

## Planned Development

Future tool-system work includes:

- Permission policies
- Confirmation prompts
- File-system tools
- Application-launching tools
- Web research tools
- Model-directed tool selection
- Multi-tool workflows
- Plugin discovery
- Hardware and robotics tools

File-system, terminal, and hardware tools will not be added until appropriate permission and safety controls are available.