# Project ATLAS Tool System

The ATLAS tool system provides a controlled and extensible mechanism for performing actions.

Tools are separate from model providers. A model generates language; a tool performs a defined operation.

ATLAS v0.9.0 expands the tool system with:

- Shared JSON-schema argument validation
- Permission-controlled execution
- Scoped filesystem tools
- Defense-in-depth validation
- Structured execution results
- Risk-aware authorization

---

## Current Architecture

```text
User request
    ↓
ATLAS Core
    ↓
JSON decoding
    ↓
Tool Registry
    ↓
Shared Argument Validation
    ↓
Permission Service
    ↓
Allow / Confirm / Deny
    ↓
Tool Executor
    ↓
Defense-in-Depth Validation
    ↓
Registered Tool
    ↓
Tool Result
```

Only registered tools can be executed.

A request must be valid and authorized before it reaches a tool implementation.

---

## Current Tools

ATLAS v0.9.0 includes eight built-in tools:

- `calculator`
- `current_time`
- `confirmation_demo`
- `list_directory`
- `file_info`
- `read_text_file`
- `create_directory`
- `write_text_file`

List registered tools from the ATLAS CLI:

```text
tools
```

Current risk behavior:

| Tool | Risk | Confirmation |
|---|---|---|
| `calculator` | Low | No |
| `current_time` | Low | No |
| `confirmation_demo` | Medium | Yes |
| `list_directory` | Low | No |
| `file_info` | Low | No |
| `read_text_file` | Low | No |
| `create_directory` | Medium | Yes |
| `write_text_file` | Medium | Yes |

Low-risk tools execute immediately after validation.

Medium-risk tools remain pending until the user explicitly approves or denies the request.

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

The expression is rejected.

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

## Filesystem Tools

ATLAS v0.9.0 introduces five scoped filesystem tools.

All filesystem tools operate only inside directories configured through:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

For the complete filesystem design, see [Secure Filesystem](filesystem.md).

### List Directory

The `list_directory` tool lists files and directories inside an approved path.

Example:

```text
tool list_directory {"path": "."}
```

The `path` argument is optional and defaults to the first configured allowed directory.

Example response:

```text
Tool list_directory result:
directory: Rocket Design (size: - bytes)
file: notes.txt (size: 13 bytes)
```

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

### File Information

The `file_info` tool returns metadata for a file or directory.

Example:

```text
tool file_info {"path": "Rocket Design/notes.txt"}
```

Example response:

```text
Tool file_info result:
Name: notes.txt
Type: file
Size: 13 bytes
Modified: 2026-08-01T17:00:00-04:00
```

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

### Read Text File

The `read_text_file` tool reads a UTF-8 text file inside an approved directory.

Example:

```text
tool read_text_file {"path": "Rocket Design/notes.txt"}
```

Example response:

```text
Tool read_text_file result: Project ATLAS
```

The tool rejects:

- Missing files
- Directories
- Files outside configured roots
- Files that exceed the read-size limit
- Invalid UTF-8 or binary content

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

On Windows, use forward slashes inside JSON paths:

```text
Rocket Design/notes.txt
```

A single backslash may be interpreted as a JSON escape sequence. Escaped backslashes also work:

```text
Rocket Design\\notes.txt
```

### Create Directory

The `create_directory` tool creates a directory inside an approved root.

Example:

```text
tool create_directory {"path": "Rocket Design"}
```

ATLAS requests confirmation before changing the filesystem.

Approve:

```text
confirm yes
```

Expected result:

```text
Tool create_directory result: Created directory: Rocket Design
```

Definition metadata:

```text
Risk level: medium
Confirmation required: yes
```

The tool rejects existing target paths.

### Write Text File

The `write_text_file` tool writes UTF-8 text inside an approved root.

Create a new file:

```text
tool write_text_file {"path": "Rocket Design/notes.txt", "content": "Project ATLAS"}
```

Approve:

```text
confirm yes
```

Expected result:

```text
Tool write_text_file result: Created file: notes.txt (13 characters)
```

Overwrite an existing file:

```text
tool write_text_file {"path": "Rocket Design/notes.txt", "content": "Updated notes", "overwrite": true}
```

The default value of `overwrite` is `false`.

Definition metadata:

```text
Risk level: medium
Confirmation required: yes
```

The tool rejects:

- Missing required arguments
- Invalid argument types
- Existing files when overwrite is false
- Directory targets
- Content exceeding the configured write limit
- Paths outside configured roots

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

## Shared Argument Validation

Location:

```text
src/atlas/tools/validation.py
```

ATLAS v0.9.0 introduces centralized validation for tool arguments.

Validation occurs twice:

```text
ATLAS Core
    ↓
Validate before permission evaluation
    ↓
Permission decision
    ↓
Tool Executor
    ↓
Validate again before execution
```

The first validation prevents invalid medium-risk requests from entering the confirmation workflow.

The second validation provides defense in depth immediately before execution.

Current supported schema features include:

- Root object schemas
- Required fields
- Unknown-field rejection
- Strings
- Booleans
- Integers
- Numbers
- Objects
- Arrays
- Null values
- Enumerations
- Nested objects
- Array-item validation

Example schema:

```python
{
    "type": "object",
    "properties": {
        "path": {
            "type": "string",
        },
        "overwrite": {
            "type": "boolean",
            "default": False,
        },
    },
    "required": ["path"],
    "additionalProperties": False,
}
```

The shared validator handles structural validation.

Individual tools still perform domain-specific validation.

Examples include:

- Restricted calculator syntax
- Filesystem path scope
- File size limits
- UTF-8 validation
- Existing-file overwrite behavior

---

## Tool Risk Levels

Risk metadata is enforced by the ATLAS permission system before execution.

ATLAS defines three tool-risk levels:

```text
low
medium
high
```

### Low Risk

Low-risk tools should not materially modify user state.

Current examples:

- Arithmetic calculation
- Reading the local time
- Listing a configured directory
- Reading a scoped UTF-8 text file
- Inspecting scoped file metadata

Low-risk tools execute automatically unless they explicitly require confirmation.

### Medium Risk

Medium-risk tools modify limited state or perform actions requiring explicit user awareness.

Current examples:

- Creating a directory
- Writing a text file
- Running the confirmation demonstration tool

Medium-risk tools require confirmation under the default policy.

### High Risk

High-risk tools may produce destructive, privileged, external, irreversible, or physical effects.

Future examples include:

- Deleting files
- Running unrestricted terminal commands
- Sending email
- Modifying system settings
- Making purchases
- Controlling physical hardware

High-risk tools are denied by the default permission policy.

---

## Tool Registry

`ToolRegistry` stores available tool implementations.

Register a tool:

```python
registry = ToolRegistry()
registry.register(CalculatorTool())
```

Register a tool with a service dependency:

```python
registry.register(ReadTextFileTool(filesystem_service))
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

The registry makes tools discoverable but does not authorize their execution.

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
- Validates arguments
- Records execution timing
- Logs the tool name and risk level
- Executes the tool
- Returns a structured result
- Converts unexpected failures into tool-system errors

The executor also exposes validation without execution:

```python
executor.validate_arguments(
    tool_name="write_text_file",
    arguments={
        "path": "notes.txt",
        "content": "ATLAS",
    },
)
```

ATLAS Core uses this method before permission evaluation.

Tool arguments should not be written to logs when they may contain sensitive information.

---

## Permission-Controlled Execution

Registering a tool does not automatically authorize execution.

Every explicit tool request follows this sequence:

```text
Tool command
    ↓
JSON decoding
    ↓
JSON-object validation
    ↓
Tool registry lookup
    ↓
Shared argument validation
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
tool create_directory {"path": "Rocket Design"}
```

Approve:

```text
confirm yes
```

Deny:

```text
confirm no
```

A pending request is cleared after either approval or denial.

Only one request may be pending at a time.

### Deny

High-risk tools are denied by the default policy.

Denied tools do not reach `ToolExecutor.execute()`.

For the complete design, see [Permission System](permissions.md).

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

ATLAS Core formats successful results as:

```text
Tool <name> result: <output>
```

A failed structured result is formatted as:

```text
Tool <name> failed: <error>
```

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

Used when arguments are missing, malformed, unsupported, unsafe, or fail tool-specific validation.

### `ToolExecutionError`

Used when a tool fails unexpectedly during execution.

### `ToolNotFoundError`

Used when the requested tool is not registered.

Filesystem tools convert filesystem validation failures into `ToolValidationError` so callers receive a consistent tool-system response.

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

- [ ] The tool name is unique and stable.
- [ ] The description accurately explains its behavior.
- [ ] The parameter schema is complete.
- [ ] Required arguments are identified.
- [ ] Unknown arguments are rejected where appropriate.
- [ ] The risk level is accurate.
- [ ] `requires_confirmation` is accurate.
- [ ] Domain-specific arguments are validated.
- [ ] Resource limits are enforced.
- [ ] Sensitive arguments are not logged.
- [ ] Permission-policy behavior is tested.
- [ ] Approval and denial behavior is tested when required.
- [ ] High-impact actions fail safely.
- [ ] Documentation is updated.

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

Confirmation-controlled tools should also test:

- The request pauses before execution
- The target state remains unchanged before approval
- Approval executes the request
- Denial prevents execution
- Invalid input fails before confirmation
- A second request cannot replace pending state

Filesystem tools should also test:

- Allowed paths
- Parent traversal
- Absolute paths outside scope
- Missing targets
- File-versus-directory errors
- Read-size limits
- Write-size limits
- UTF-8 behavior
- Overwrite protection

Run tool tests:

```powershell
pytest tests\test_tools.py
```

Run shared validation tests:

```powershell
pytest tests\test_tool_validation.py
```

Run filesystem tests:

```powershell
pytest tests\test_filesystem.py
```

Run application integration tests:

```powershell
pytest tests\test_app.py
```

Run the entire suite:

```powershell
pytest
```

---

## Security Requirements

A tool must never assume model output or user-provided JSON is safe.

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
11. Remain inside configured resource scopes.
12. Avoid authorizing itself.

Tool availability does not imply authorization.

Permission approval does not replace subsystem-specific safety validation.

---

## Current Limitations

The v0.9.0 tool system does not yet support:

- Model-directed tool selection
- Automatic multi-tool workflows
- Parallel tool execution
- Persistent permission grants
- High-risk approval
- Dynamic plugin discovery
- File deletion
- File renaming
- File moving
- File copying
- Application launching
- Terminal commands
- Remote-service tools
- Hardware tools

These capabilities require additional planning, authorization, and isolation controls.

---

## Planned Development

Future tool-system work includes:

- Model-directed tool selection
- Multi-tool workflows
- Agent execution loops
- Application-launching tools
- Web research tools
- Document tools
- Engineering tools
- Plugin discovery
- Scoped permission grants
- Desktop automation
- Hardware and robotics tools

Future file, terminal, external-service, and hardware tools will build on:

- Shared schema validation
- Permission-controlled execution
- Scoped resource services
- Structured logging
- Security-focused testing

High-risk tools remain denied until stronger authorization and safety controls are implemented.
