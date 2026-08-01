# Project ATLAS Permission System

The ATLAS permission system controls whether a tool may execute immediately, requires explicit user confirmation, or must be denied.

The system was introduced in ATLAS v0.8.0 to create a security boundary between tool requests and tool execution.

---

## Purpose

Registered tools can eventually interact with files, applications, external services, smart devices, and physical hardware.

Tool registration alone is not sufficient authorization.

Before a tool executes, ATLAS evaluates:

- The tool name
- The tool risk level
- Whether the tool explicitly requires confirmation
- The active permission policy
- The user's confirmation response, when required

This prevents tools from executing solely because they are available in the registry.

---

## Permission Architecture

```text
User requests tool
        ↓
ATLAS Core
        ↓
Tool Registry
        ↓
Tool Definition
        ↓
Permission Service
        ↓
Permission Policy
        ↓
┌─────────────┬─────────────┬─────────────┐
│ Allow       │ Confirm     │ Deny        │
│ Execute now │ Wait        │ Block       │
└─────────────┴─────────────┴─────────────┘
        ↓
Tool Executor
        ↓
Tool Result
```

The permission system is intentionally separate from individual tool implementations.

A tool describes its risk and confirmation requirements. The permission policy decides what ATLAS should do with that metadata.

---

## Permission Decisions

ATLAS defines three permission decisions:

```text
allow
confirm
deny
```

### Allow

The tool may execute immediately.

The default policy allows a tool when:

- Its risk level is `low`
- It does not explicitly require confirmation

Example:

```text
tool calculator {"expression": "12 * 8"}
```

The calculator is low risk and does not require confirmation, so it executes immediately.

---

### Confirm

The request is stored temporarily until the user explicitly approves or denies it.

The default policy requires confirmation when:

- The tool risk level is `medium`
- The tool definition sets `requires_confirmation=True`

Example:

```text
tool confirmation_demo {"message": "Approved action"}
```

ATLAS responds with a confirmation request:

```text
Tool confirmation_demo requires confirmation.
Risk level: medium.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

Approve the request:

```text
confirm yes
```

Deny the request:

```text
confirm no
```

---

### Deny

The tool is blocked and does not reach the executor.

The default policy denies:

- All high-risk tools

High-risk tools cannot currently be approved through the standard confirmation flow.

This is intentional. High-risk actions require stronger authorization controls than a single yes-or-no prompt.

---

## Default Policy

ATLAS v0.8.0 uses the following default policy:

| Tool condition | Decision |
|---|---|
| Low risk and no confirmation flag | Allow |
| Medium risk | Confirm |
| Explicit confirmation flag | Confirm |
| High risk | Deny |

High-risk denial takes priority over confirmation metadata.

A high-risk tool remains denied even if its definition also sets:

```python
requires_confirmation = True
```

---

## Risk Levels

ATLAS uses three tool-risk levels.

### Low Risk

Low-risk tools should not modify important state or expose sensitive information.

Examples:

- Arithmetic calculations
- Reading the current local time
- Reading non-sensitive public information

Low-risk tools may execute immediately unless they explicitly request confirmation.

---

### Medium Risk

Medium-risk tools may modify state or perform actions with limited consequences.

Future examples may include:

- Creating a directory
- Renaming a file
- Opening an application
- Writing a local note
- Sending a desktop notification

Medium-risk tools require explicit confirmation.

---

### High Risk

High-risk tools may cause destructive, irreversible, external, privileged, or physical effects.

Future examples may include:

- Deleting files
- Running unrestricted terminal commands
- Sending email
- Modifying operating-system settings
- Making purchases
- Unlocking doors
- Controlling motors or robotics hardware

High-risk tools are denied by default in v0.8.0.

---

## Permission Models

The permission subsystem defines several data models.

### `PermissionDecision`

Represents the result of policy evaluation:

```python
class PermissionDecision(StrEnum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    DENY = "deny"
```

### `PermissionEvaluation`

Represents one completed policy decision:

```python
@dataclass(frozen=True)
class PermissionEvaluation:
    tool_name: str
    risk_level: ToolRiskLevel
    decision: PermissionDecision
    reason: str
```

### `PendingToolRequest`

Represents a tool request waiting for confirmation:

```python
@dataclass(frozen=True)
class PendingToolRequest:
    tool_name: str
    arguments: dict[str, Any]
    risk_level: ToolRiskLevel
```

Pending arguments remain inside the running ATLAS process until the request is approved, denied, or replaced by a future lifecycle policy.

---

## Permission Policy

`PermissionPolicy` contains the default authorization rules.

Location:

```text
src/atlas/permissions/policy.py
```

The policy evaluates a `ToolDefinition` and returns a `PermissionEvaluation`.

The policy does not execute tools.

Its only responsibility is deciding whether a request should be allowed, confirmed, or denied.

---

## Permission Service

`PermissionService` coordinates policy evaluation and permission auditing.

Location:

```text
src/atlas/permissions/service.py
```

Responsibilities:

- Evaluate tool definitions
- Return permission decisions
- Log allow, confirm, and deny outcomes
- Record user approval or denial
- Avoid logging complete tool arguments

The permission service does not directly store pending requests. ATLAS Core currently owns pending confirmation state.

---

## Confirmation Lifecycle

A confirmation-controlled request follows this lifecycle:

```text
Tool command received
        ↓
Arguments parsed
        ↓
Tool found in registry
        ↓
Permission evaluated
        ↓
Request stored as pending
        ↓
User chooses yes or no
        ↓
Pending state cleared
        ↓
Execute or deny
```

### Approval

When the user enters:

```text
confirm yes
```

ATLAS:

1. Confirms that a request is pending.
2. Records the approval.
3. Clears the pending state.
4. Sends the saved request to the tool executor.
5. Returns the tool result.

### Denial

When the user enters:

```text
confirm no
```

ATLAS:

1. Confirms that a request is pending.
2. Records the denial.
3. Clears the pending state.
4. Does not call the tool executor.
5. Reports that execution was denied.

### Invalid Confirmation Input

Inputs such as:

```text
confirm maybe
confirm later
confirm okay
```

do not execute the tool.

ATLAS accepts only:

```text
confirm yes
confirm no
```

The pending request remains available after unclear confirmation input.

---

## Pending-Request Protection

ATLAS allows only one pending tool request at a time.

When one request is waiting for confirmation, a second confirmation-controlled request is rejected.

This prevents a new request from silently replacing the request the user originally reviewed.

The user must first enter:

```text
confirm yes
```

or:

```text
confirm no
```

---

## Audit Logging

Permission activity is recorded through the structured logging subsystem.

Logs may include:

- Tool name
- Tool risk level
- Permission decision
- Confirmation requirement
- User approval or denial
- Request ID
- Execution success or failure

Logs must not include:

- Complete sensitive tool arguments
- API keys
- Passwords
- Authentication tokens
- File contents
- Private message contents
- Memory contents

Example conceptual log entries:

```text
Permission decision evaluated.
tool=confirmation_demo
risk=medium
decision=confirm
```

```text
Tool confirmation resolved.
tool=confirmation_demo
approved=true
```

---

## Privacy

The permission system stores pending tool arguments only in process memory.

ATLAS v0.8.0 does not persist pending confirmations to SQLite.

Therefore:

- Pending requests disappear when ATLAS exits
- Pending requests are not restored after restart
- Pending arguments are not stored in conversation history
- Complete arguments are not written to logs

---

## Tool-Execution Boundary

Permission checks occur before `ToolExecutor.execute()`.

A denied request must never reach the executor.

A confirmation-controlled request must not reach the executor until approval is received.

The expected sequence is:

```text
Parse
→ Find tool
→ Evaluate permission
→ Authorize
→ Execute
```

Not:

```text
Parse
→ Execute
→ Ask permission afterward
```

---

## Failure Behavior

ATLAS should fail safely.

Examples:

- Unknown tool: reject the request
- Invalid JSON: reject before permission evaluation
- Arguments are not a JSON object: reject
- No pending request: reject confirmation command
- Unclear confirmation: do not execute
- High-risk tool: deny before execution
- Missing permission service: log a warning

Future releases may make the permission service mandatory rather than optional.

---

## Current Demonstration Tool

ATLAS v0.8.0 includes:

```text
confirmation_demo
```

This tool is classified as:

```text
Risk: medium
Confirmation: required
```

It exists only to test the permission and confirmation architecture without modifying files or controlling the computer.

Example:

```text
tool confirmation_demo {"message": "Permission granted"}
confirm yes
```

Expected result:

```text
Tool confirmation_demo result: Permission granted
```

---

## Testing Requirements

Permission tests should cover:

- Low-risk allow decision
- Medium-risk confirmation decision
- Explicit confirmation metadata
- High-risk denial
- Permission-service evaluation
- Confirmation approval
- Confirmation denial
- Confirmation without a pending request
- Invalid confirmation input
- Prevention of pending-request replacement
- Immediate low-risk execution
- Denied requests not reaching execution
- Risk metadata on built-in tools

Run:

```powershell
pytest tests\test_permissions.py
pytest tests\test_app.py
pytest tests\test_tools.py
```

Run the full suite:

```powershell
pytest
```

---

## Current Limitations

ATLAS v0.8.0 does not yet support:

- Persistent permission grants
- Allow-always decisions
- Per-tool user policies
- Per-directory permissions
- Expiring approvals
- User authentication
- Operating-system privilege separation
- Cryptographic authorization
- Multiple pending requests
- Remote approval
- Hardware emergency-stop integration
- High-risk approval

These capabilities require future security work.

---

## Future Development

Planned permission-system expansions include:

- Scoped file permissions
- Trusted-directory configuration
- Session-based approvals
- Expiring grants
- Tool-specific policies
- User identity and authentication
- Role-based permissions
- External-action previews
- Permission history
- Emergency shutdown
- Hardware safety interlocks
- Separate policies for local and remote clients

---

## Security Principle

> Tool availability does not imply tool authorization.

Every future ATLAS tool should pass through permission evaluation before execution.