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

ATLAS v0.8.0 includes three built-in tools:

- `calculator`
- `current_time`
- `confirmation_demo`

List registered tools from the ATLAS CLI:

```text
tools
```

The calculator and current-time tools are low risk and execute immediately.

The confirmation demonstration tool is medium risk and requires explicit approval.

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

## Confirmation Demonstration Tool

The `confirmation_demo` tool validates the ATLAS permission and confirmation workflow without modifying files or controlling the operating system.

Example request:

```text
tool confirmation_demo {"message": "Approved action"}
```

ATLAS pauses and requests confirmation.

Approve:

```text
confirm yes
```

Expected result:

```text
Tool confirmation_demo result: Approved action
```

Deny:

```text
confirm no
```

Expected result:

```text
Tool confirmation_demo execution was denied.
```

Definition metadata:

```text
Risk level: medium
Confirmation required: yes
```

This demonstration tool is intended for development and security testing.

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

Risk metadata is enforced by the ATLAS permission system before execution. It is no longer descriptive metadata only.

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

## Permission-Controlled Execution

Starting with ATLAS v0.8.0, registering a tool does not automatically authorize its execution.

Every explicit tool request follows this sequence:

```text
Tool command
    ↓
JSON validation
    ↓
Tool registry lookup
    ↓
Permission evaluation
    ↓
Allow, confirm, or deny
    ↓
Tool executor
```

The permission system evaluates:

- `risk_level`
- `requires_confirmation`
- The active permission policy

### Allow

Low-risk tools that do not require confirmation execute immediately.

Example:

```text
tool calculator {"expression": "2 + 2"}
```

### Confirm

Medium-risk tools and tools explicitly marked for confirmation pause before execution.

Example:

```text
tool confirmation_demo {"message": "Approved action"}
```

Approve:

```text
confirm yes
```

Deny:

```text
confirm no
```

### Deny

High-risk tools are denied by the default v0.8.0 policy.

Denied tools do not reach `ToolExecutor.execute()`.

For the complete design, see [Permission System](permissions.md).

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

Before registering a new tool, verify:

- [ ] The risk level is accurate.
- [ ] `requires_confirmation` is accurate.
- [ ] All arguments are validated.
- [ ] Unknown arguments are rejected where appropriate.
- [ ] Sensitive arguments are not logged.
- [ ] Permission-policy behavior is tested.
- [ ] Approval and denial behavior is tested when confirmation is required.
- [ ] High-impact actions fail safely.

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

- File-system tools
- Application-launching tools
- Web research tools
- Model-directed tool selection
- Multi-tool workflows
- Plugin discovery
- Scoped permission grants
- Hardware and robotics tools

File-system, terminal, external-service, and hardware tools will build on the v0.8.0 permission system.

High-risk tools remain denied until stronger authorization and safety controls are implemented.