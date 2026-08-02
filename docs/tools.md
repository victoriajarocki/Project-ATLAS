# Project ATLAS Tool System

The ATLAS tool system provides a controlled, extensible mechanism for performing defined operations.

Tools are separate from model providers:

- A model interprets a request and may select a tool.
- A tool performs one specific operation.
- The permission system determines whether execution is allowed.
- The executor validates and runs authorized tools.

ATLAS v1.0.0 extends the tool system with:

- Natural-language tool selection
- Structured agent decisions
- Dynamic tool catalogs
- JSON-schema-constrained Ollama output
- Shared argument validation
- Permission-controlled execution
- Deterministic routing for recognized state-changing requests
- Scoped filesystem tools
- Defense-in-depth validation
- Structured execution results
- Trusted tool-result responses
- Backward-compatible explicit tool commands

---

## Current Architecture

Natural-language tool execution follows:

```text
User request
    ↓
AtlasApp
    ↓
Deterministic safety routing
    ↓
Agent Service
    ↓
Agent Prompt Builder
    ↓
Model Provider
    ↓
Structured JSON Decision
    ↓
Agent Decision Parser
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
Trusted Tool Result
```

Explicit tool execution remains available:

```text
Explicit tool command
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
Registered Tool
    ↓
Tool Result
```

Only registered tools can be executed.

A request must be structurally valid, authorized, and within subsystem-specific safety boundaries before it reaches a tool implementation.

---

## Agent Tool Selection

ATLAS v1.0.0 allows the model to select a registered tool from a natural-language request.

For example, the user may ask:

```text
What is 347 multiplied by 982?
```

ATLAS can select:

```text
calculator
```

with arguments equivalent to:

```json
{
  "expression": "347 * 982"
}
```

The user does not need to enter:

```text
tool calculator {"expression":"347 * 982"}
```

Similarly:

```text
What files are in my workspace?
```

may select:

```text
list_directory
```

with:

```json
{
  "path": "."
}
```

Tool selection is not unrestricted.

The agent must:

- Select exactly one registered tool
- Use the tool's exact registered name
- Supply arguments matching the tool schema
- Pass shared validation
- Pass permission evaluation
- Remain within tool-specific safety boundaries

Malformed or invented tool requests are rejected.

---

## Structured Agent Decisions

Agent decisions use a structured JSON format.

A direct response resembles:

```json
{
  "decision": "respond",
  "response": "The capital of Poland is Warsaw."
}
```

A tool-use response resembles:

```json
{
  "decision": "use_tool",
  "tool": {
    "name": "calculator",
    "arguments": {
      "expression": "12 * 4"
    }
  }
}
```

The parser rejects:

- Invalid JSON
- Missing required fields
- Unknown decision types
- Unknown fields
- Missing tool requests
- Invalid tool names
- Invalid argument structures

Model output never reaches execution without validation.

---

## Deterministic Safety Routing

Some clearly recognized state-changing requests are routed without allowing the model to decide whether the action occurred.

Examples include:

```text
Create a folder called Rocket Design.
```

and:

```text
Create a file called hello.txt that says Hello World.
```

These requests are converted directly into structured tool requests for:

```text
create_directory
```

or:

```text
write_text_file
```

They still pass through:

```text
Tool lookup
    ↓
Argument validation
    ↓
Permission evaluation
    ↓
Confirmation
    ↓
Execution
```

This prevents a model from falsely claiming that a file or folder was created without executing the corresponding tool.

Current deterministic routing is intentionally narrow and currently targets recognized English file-creation and directory-creation requests.

---

## Trusted Tool Results

After successful execution, ATLAS returns the trusted output from the tool directly.

The v1.0.0 agent does not make a second model call to rewrite tool results.

This design:

- Reduces response latency
- Prevents reasoning leakage
- Prevents prompt leakage
- Avoids the model misrepresenting the result
- Preserves exact tool output
- Simplifies testing

For example, the calculator may return:

```text
340754
```

A directory-creation tool may return:

```text
Created directory: Rocket Design
```

A file-writing tool may return:

```text
Created file: hello.txt (11 characters)
```

Explicit tool commands continue to use the format:

```text
Tool <name> result: <output>
```

---

## Current Tools

ATLAS v1.0.0 includes eight built-in tools:

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

High-risk tools are denied by the default permission policy.

---

## Calculator

The calculator evaluates restricted arithmetic expressions.

### Natural-Language Example

```text
What is 347 multiplied by 982?
```

Possible result:

```text
340754
```

### Explicit Command

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

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

---

## Current Time

The current-time tool returns the local date and time of the computer running ATLAS.

### Natural-Language Example

```text
What time is it?
```

Example result:

```text
Current local time

Saturday, August 01, 2026
8:10:48 PM EDT
```

### Explicit Command

```text
tool current_time {}
```

The tool accepts no arguments.

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

The result is based on:

```python
datetime.now().astimezone()
```

This uses the timezone configured on the computer running ATLAS.

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

ATLAS includes five scoped filesystem tools.

All filesystem tools operate only inside directories configured through:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

For the complete filesystem design, see [Secure Filesystem](filesystem.md).

---

### List Directory

The `list_directory` tool lists files and directories inside an approved path.

### Natural-Language Example

```text
What files are in my workspace?
```

Possible result:

```text
file: .gitkeep (size: 0 bytes)
file: agent-test.txt (size: 27 bytes)
```

### Explicit Command

```text
tool list_directory {"path": "."}
```

Example response:

```text
Tool list_directory result:
directory: Rocket Design (size: - bytes)
file: notes.txt (size: 13 bytes)
```

The `path` argument may be omitted when supported by the tool implementation, but agent-generated requests should normally provide:

```json
{
  "path": "."
}
```

when the user refers to the configured workspace.

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

---

### File Information

The `file_info` tool returns metadata for a file or directory.

### Natural-Language Example

```text
How large is Rocket Design/notes.txt?
```

The model may select `file_info`.

### Explicit Command

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

---

### Read Text File

The `read_text_file` tool reads a UTF-8 text file inside an approved directory.

### Natural-Language Example

```text
Read agent-test.txt.
```

Possible result:

```text
Project ATLAS agent test.
```

### Explicit Command

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
- Invalid UTF-8 content
- Binary content that cannot be decoded as UTF-8

Definition metadata:

```text
Risk level: low
Confirmation required: no
```

On Windows, use forward slashes inside JSON paths:

```text
Rocket Design/notes.txt
```

A single backslash may be interpreted as a JSON escape sequence.

Escaped backslashes also work:

```text
Rocket Design\\notes.txt
```

Forward slashes are recommended.

---

### Create Directory

The `create_directory` tool creates a directory inside an approved root.

### Natural-Language Example

```text
Create a folder called Rocket Design.
```

ATLAS should return:

```text
Tool create_directory requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

Approve:

```text
confirm yes
```

Expected agent result:

```text
Created directory: Rocket Design
```

### Explicit Command

```text
tool create_directory {"path": "Rocket Design"}
```

After approval:

```text
Tool create_directory result: Created directory: Rocket Design
```

Definition metadata:

```text
Risk level: medium
Confirmation required: yes
```

The tool rejects:

- Existing target paths
- Paths outside configured roots
- Invalid path values
- Targets whose parent path is invalid

No directory is created before approval.

---

### Write Text File

The `write_text_file` tool writes UTF-8 text inside an approved root.

### Natural-Language Example

```text
Create a file called hello.txt that says Hello World.
```

ATLAS should return:

```text
Tool write_text_file requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

Approve:

```text
confirm yes
```

Expected agent result:

```text
Created file: hello.txt (11 characters)
```

### Explicit Command

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
- Unknown arguments
- Existing files when overwrite is false
- Directory targets
- Content exceeding the configured write limit
- Paths outside configured roots

No file is modified before approval.

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

The agent, explicit command system, registry, permission system, and executor all rely on this shared interface.

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

Descriptions should clearly tell both developers and models what the tool does.

Parameter schemas should be precise enough to prevent ambiguous argument generation.

---

## Dynamic Tool Catalog

The agent prompt builder creates its available-tool catalog directly from registered `ToolDefinition` objects.

The catalog contains:

- Tool name
- Description
- Parameter schema
- Risk level
- Confirmation requirement

Conceptually:

```text
Tool Registry
    ↓
List Tool Definitions
    ↓
Serialize Safe Metadata
    ↓
Insert Into Agent Prompt
```

This ensures that:

- The agent sees only tools that are actually registered
- Tool names remain synchronized with the application
- Argument schemas remain synchronized
- Risk and confirmation metadata are visible to the model
- New tools can be added without hardcoding prompt entries

The catalog does not authorize execution.

It only informs the model about available capabilities.

---

## Shared Argument Validation

Location:

```text
src/atlas/tools/validation.py
```

ATLAS uses centralized validation for tool arguments.

For explicit tool requests:

```text
AtlasApp
    ↓
Validate before permission evaluation
    ↓
Permission decision
    ↓
Tool Executor
    ↓
Validate again before execution
```

For model-selected tool requests:

```text
Agent Decision
    ↓
Tool Registry Lookup
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

Individual tools remain responsible for domain-specific validation.

Examples include:

- Restricted calculator syntax
- Filesystem path scope
- File-size limits
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
    arguments={
        "expression": "2 + 2",
    },
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

Both AtlasApp and AgentService use shared validation before permission evaluation.

Tool arguments should not be written to logs when they may contain sensitive information.

---

## Permission-Controlled Execution

Registering a tool does not automatically authorize execution.

Every tool request passes through the permission system.

The system evaluates:

- `risk_level`
- `requires_confirmation`
- The active permission policy

### Allow

Low-risk tools that do not require confirmation execute immediately.

Natural-language example:

```text
What is 2 + 2?
```

Explicit example:

```text
tool calculator {"expression": "2 + 2"}
```

### Confirm

Medium-risk tools and tools explicitly marked for confirmation pause before execution.

Natural-language example:

```text
Create a folder called Rocket Design.
```

Explicit example:

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

Unrelated requests are blocked while confirmation is pending.

### Deny

High-risk tools are denied by the default policy.

Denied tools do not reach `ToolExecutor.execute()`.

For the complete design, see [Permission System](permissions.md).

---

## Agent-Selected Confirmation Workflow

A model-selected medium-risk request follows:

```text
Natural-language request
    ↓
Agent or deterministic router creates tool request
    ↓
Tool lookup
    ↓
Argument validation
    ↓
Permission decision: Confirm
    ↓
Agent pending request stored
    ↓
User enters confirm yes or confirm no
```

After approval:

```text
Pending request
    ↓
Permission confirmation recorded
    ↓
Tool Executor
    ↓
Tool implementation
    ↓
Trusted tool output
    ↓
Conversation storage
    ↓
User response
```

After denial:

```text
Pending request
    ↓
Permission denial recorded
    ↓
No execution
    ↓
Pending state cleared
```

The original model decision is not regenerated after approval.

The exact saved tool name and arguments are executed once.

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

For explicit commands, AtlasApp formats successful results as:

```text
Tool <name> result: <output>
```

For agent-selected requests, AgentService returns the trusted tool output directly.

A failed structured result may be formatted as:

```text
Tool <name> failed: <error>
```

Unexpected exceptions are converted into controlled tool or agent errors.

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

AgentService converts tool-system failures into agent-level failures when the request originated through the agent.

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

Because the agent catalog is generated dynamically, a registered tool automatically becomes visible to the agent.

That does not mean the model will use it correctly without:

- A clear description
- A precise schema
- Accurate risk metadata
- Agent prompt tests
- Integration testing

Add tests before considering the tool complete.

---

## Tool Development Checklist

Before registering a new tool, verify:

```text
[ ] The tool name is unique and stable.
[ ] The description accurately explains its behavior.
[ ] The description is clear enough for model selection.
[ ] The parameter schema is complete.
[ ] Required arguments are identified.
[ ] Unknown arguments are rejected where appropriate.
[ ] The risk level is accurate.
[ ] requires_confirmation is accurate.
[ ] Domain-specific arguments are validated.
[ ] Resource limits are enforced.
[ ] Sensitive arguments are not logged.
[ ] Permission-policy behavior is tested.
[ ] Approval and denial behavior is tested when required.
[ ] Agent-selected execution is tested.
[ ] Explicit execution is tested.
[ ] High-impact actions fail safely.
[ ] Documentation is updated.
```

---

## Tool Test Requirements

Every tool should test:

- Registration
- Definition metadata
- Valid input
- Missing arguments
- Incorrect argument types
- Unsupported arguments
- Boundary values
- Failure behavior
- Security-sensitive input
- Correct risk metadata
- Explicit command execution
- Agent-selected execution when relevant

Confirmation-controlled tools should also test:

- The request pauses before execution
- The target state remains unchanged before approval
- Approval executes the saved request
- Denial prevents execution
- Invalid input fails before confirmation
- A second request cannot replace pending state
- Pending state is cleared after approval
- Pending state is cleared after denial

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

Run application tool tests:

```powershell
pytest tests\test_app.py
```

Run agent service tests:

```powershell
pytest tests\test_agent_service.py
```

Run application-level agent tests:

```powershell
pytest tests\test_app_agent.py
```

Run the complete suite:

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
13. Behave identically whether selected explicitly or by the agent.
14. Never trust a model claim that execution occurred.
15. Return output that accurately reflects the completed operation.

Tool availability does not imply authorization.

Permission approval does not replace subsystem-specific validation.

A valid agent decision does not replace permission evaluation.

---

## Current Limitations

The v1.0.0 tool system supports natural-language selection but remains intentionally constrained.

Current limitations include:

- One model-selected tool per request
- No automatic multi-tool workflow
- No recursive agent loop
- No parallel tool execution
- No persistent permission grants
- No high-risk approval flow
- No dynamic plugin discovery
- No file deletion
- No file renaming
- No file moving
- No file copying
- No application launching
- No terminal commands
- No web tools
- No remote-service tools
- No hardware tools
- No background execution
- No scheduled tool execution

Deterministic routing currently handles a limited set of recognized English file and directory creation requests.

Tool-assisted agent responses currently return trusted raw tool output rather than model-generated summaries.

These limitations keep the first agent release bounded, testable, and secure.

---

## Planned Development

Future tool-system work may include:

- Multi-step tool workflows
- Bounded agent execution loops
- Replanning after tool results
- Agent step limits
- Repeated confirmation handling
- Failed-tool recovery
- Tool-result summary formatting
- Application-launching tools
- Web research tools
- Document tools
- Engineering tools
- Plugin discovery
- Scoped permission grants
- Desktop automation
- Hardware and robotics tools
- Scheduled tools
- Remote-service integrations

Future file, terminal, external-service, and hardware tools will continue building on:

- Shared schema validation
- Structured agent decisions
- Permission-controlled execution
- Scoped resource services
- Structured logging
- Security-focused testing
- Explicit user authorization

High-risk tools remain denied until stronger authorization, isolation, and safety controls are implemented.

---

## Summary

The ATLAS v1.0.0 tool system supports both explicit and natural-language execution.

Its core guarantees are:

- Only registered tools may execute
- Arguments are validated before authorization
- Permissions are evaluated before execution
- Medium-risk actions require confirmation
- High-risk actions are denied
- Filesystem tools remain scoped
- The executor validates again before execution
- Agent-selected tools use the same controls as explicit commands
- Trusted tool output is returned after execution
- State-changing actions cannot be silently performed

The tool framework remains the execution foundation for future agent, automation, desktop, web, voice, vision, and robotics capabilities.