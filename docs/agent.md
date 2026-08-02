# Project ATLAS Agent System

The ATLAS agent system converts natural-language requests into controlled application decisions.

Version 1.0.0 introduces the first agent foundation for Project ATLAS.

Before v1.0.0, users primarily interacted with tools through explicit commands such as:

```text
tool calculator {"expression":"12 * 4"}
```

The agent system allows equivalent requests to be expressed naturally:

```text
What is 12 multiplied by 4?
```

ATLAS can then:

1. Interpret the request.
2. Decide whether a tool is required.
3. Select one registered tool.
4. Produce structured tool arguments.
5. Validate the request.
6. Apply permission policy.
7. Execute or pause for confirmation.
8. Return a trusted result.

The v1.0.0 agent is intentionally constrained.

It is not an unrestricted autonomous system.

Current limitations include:

- One model-selected tool per request
- No recursive planning loop
- No background execution
- No unrestricted shell access
- No unrestricted filesystem access
- No autonomous multi-step workflows
- No persistent plans

These limitations keep the first agent release predictable, testable, and secure.

---

# Purpose

The agent subsystem exists to coordinate natural-language intent with existing ATLAS capabilities.

It does not replace:

- Model providers
- Tool validation
- Permission evaluation
- Tool execution
- Filesystem scope enforcement
- Memory storage
- Conversation storage

Instead, the agent connects those systems through a controlled decision pipeline.

The agent is responsible for deciding:

```text
Should ATLAS respond directly?

or

Should ATLAS request one registered tool?
```

The agent is not responsible for deciding whether an action is authorized.

Authorization belongs to the permission subsystem.

---

# Location

The agent subsystem is located in:

```text
src/atlas/agent/
```

Current files include:

```text
src/atlas/agent/
├── __init__.py
├── exceptions.py
├── models.py
├── parser.py
├── prompt.py
└── service.py
```

Agent-related tests are located in:

```text
tests/
├── test_agent_models.py
├── test_agent_parser.py
├── test_agent_prompt.py
├── test_agent_service.py
└── test_app_agent.py
```

---

# High-Level Architecture

The v1.0.0 agent execution pipeline is:

```text
User Request
    ↓
Command-Line Interface
    ↓
AtlasApp
    ↓
Built-in Command Detection
    ↓
Deterministic Safety Routing
    ↓
Agent Service
    ↓
Agent Prompt Builder
    ↓
Model Provider
    ↓
Structured Agent Decision
    ↓
Agent Decision Parser
    ↓
Tool Registry Lookup
    ↓
Argument Validation
    ↓
Permission Evaluation
    ↓
Allow / Confirm / Deny
    ↓
Tool Executor
    ↓
Trusted Tool Result
    ↓
Conversation Storage
    ↓
User Response
```

Each stage performs a separate responsibility.

This separation improves:

- Security
- Testability
- Maintainability
- Failure isolation
- Provider independence
- Tool extensibility

---

# Agent Responsibilities

The agent subsystem is responsible for:

- Building structured model prompts
- Providing the model with available tools
- Requesting a structured decision
- Parsing the returned JSON
- Producing typed decision models
- Rejecting malformed decisions
- Verifying selected tool names
- Validating generated arguments
- Coordinating permission evaluation
- Coordinating confirmed execution
- Returning trusted tool output
- Preserving conversation context
- Supporting deterministic action routing

The agent subsystem is not responsible for:

- Implementing tool behavior
- Performing filesystem operations directly
- Defining permission policy
- Reading environment variables directly
- Managing SQLite repositories directly
- Bypassing confirmation
- Authorizing high-risk tools
- Executing arbitrary code

---

# Agent Components

## Agent Models

Location:

```text
src/atlas/agent/models.py
```

Agent models represent validated decisions and pending requests.

The model layer prevents the rest of the application from passing raw dictionaries throughout the system.

Current concepts include:

- Decision type
- Direct response
- Tool request
- Agent run result
- Pending agent request

Typical decision types are:

```text
respond
use_tool
```

A direct-response decision contains user-facing response text.

A tool-use decision contains:

- Registered tool name
- Structured argument object

Typed models reduce ambiguity and make invalid states easier to detect.

---

## Agent Exceptions

Location:

```text
src/atlas/agent/exceptions.py
```

Agent-specific errors are separated from:

- Model errors
- Tool errors
- Permission errors
- Filesystem errors
- Conversation errors
- Memory errors

Current agent exception concepts include:

```text
AgentError
AgentConfigurationError
AgentDecisionError
AgentParsingError
```

### `AgentError`

Base error for agent failures.

### `AgentConfigurationError`

Used when the agent is invoked with invalid configuration or empty input.

### `AgentDecisionError`

Used when a parsed decision is structurally valid but cannot be executed safely.

Examples include:

- Unknown tool name
- Missing tool request
- Invalid generated arguments
- Inconsistent decision fields

### `AgentParsingError`

Used when model output cannot be parsed into a valid decision.

Examples include:

- Invalid JSON
- Non-object JSON
- Unknown decision type
- Missing required fields
- Unknown fields
- Invalid field types

---

# Prompt Builder

Location:

```text
src/atlas/agent/prompt.py
```

The `AgentPromptBuilder` creates the structured prompt used for the first agent decision.

The prompt includes:

- System instructions
- Registered tool catalog
- Tool descriptions
- Tool parameter schemas
- Tool risk metadata
- Tool confirmation metadata
- Conversation context
- Current user request
- Raw JSON output requirement

Conceptual prompt structure:

```text
SYSTEM INSTRUCTIONS

AVAILABLE TOOLS

CONVERSATION CONTEXT

CURRENT USER REQUEST

RETURN ONE RAW JSON OBJECT ONLY
```

The prompt builder receives tool definitions dynamically from the registry.

This prevents the prompt from becoming disconnected from the actual application.

---

## Dynamic Tool Catalog

The agent does not maintain a hard-coded tool list.

Instead:

```text
Tool Registry
    ↓
List Registered Definitions
    ↓
Serialize Prompt-Safe Metadata
    ↓
Add to Agent Prompt
```

The model receives:

- Tool name
- Description
- JSON parameter schema
- Risk level
- Confirmation requirement

Example serialized tool definition:

```json
{
  "name": "calculator",
  "description": "Evaluate a basic arithmetic expression.",
  "parameters": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string"
      }
    },
    "required": [
      "expression"
    ],
    "additionalProperties": false
  },
  "risk_level": "low",
  "requires_confirmation": false
}
```

The tool catalog informs the model.

It does not authorize execution.

---

## Prompt Safety Rules

Current prompt instructions emphasize that the model must:

- Use only registered tools
- Use exact tool names
- Match parameter schemas
- Avoid inventing files or results
- Avoid claiming an action occurred without execution
- Use filesystem tools for filesystem actions
- Use the current-time tool for current local time
- Use the calculator for arithmetic
- Use the configured workspace when the user refers to their workspace
- Return only one raw JSON object
- Avoid Markdown fences
- Avoid explanations outside the JSON object

Prompt instructions improve model behavior but are not treated as the primary security boundary.

Application-level enforcement remains mandatory.

---

# Structured Agent Decisions

The agent requests one of two decision types.

## Direct Response

A direct response resembles:

```json
{
  "decision": "respond",
  "response": "The capital of Poland is Warsaw."
}
```

A direct response is appropriate when:

- No tool is required
- The answer does not depend on live local state
- The user is asking a conversational or knowledge question
- The request does not require an external action

---

## Tool Request

A tool request resembles:

```json
{
  "decision": "use_tool",
  "tool": {
    "name": "calculator",
    "arguments": {
      "expression": "347 * 982"
    }
  }
}
```

A tool request is appropriate when:

- A registered tool provides a more reliable answer
- The user requests a supported action
- Current local state must be inspected
- Files must be read or listed
- Arithmetic should be calculated
- Local time must be retrieved

The v1.0.0 schema permits one selected tool per decision.

---

# Structured Decision Schema

The agent service supplies a JSON schema to providers that support structured output.

Conceptually:

```json
{
  "type": "object",
  "properties": {
    "decision": {
      "type": "string",
      "enum": [
        "respond",
        "use_tool"
      ]
    },
    "response": {
      "type": [
        "string",
        "null"
      ]
    },
    "tool": {
      "anyOf": [
        {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "arguments": {
              "type": "object"
            }
          },
          "required": [
            "name",
            "arguments"
          ],
          "additionalProperties": false
        },
        {
          "type": "null"
        }
      ]
    }
  },
  "required": [
    "decision"
  ],
  "additionalProperties": false
}
```

The schema constrains provider output but does not replace the parser.

The parser still validates the response after generation.

---

# Agent Decision Parser

Location:

```text
src/atlas/agent/parser.py
```

The parser converts raw model output into typed agent decisions.

Conceptual process:

```text
Raw Model Output
    ↓
Trim Output
    ↓
Remove Supported Wrapping
    ↓
Parse JSON
    ↓
Require Root Object
    ↓
Validate Decision Type
    ↓
Validate Required Fields
    ↓
Reject Unknown Fields
    ↓
Build Typed Decision
```

The parser rejects malformed or ambiguous output before tool lookup.

---

## Parser Validation

The parser should reject:

- Empty output
- Invalid JSON
- JSON arrays
- JSON strings
- JSON numbers
- Missing `decision`
- Unsupported decision values
- Unknown top-level fields
- Missing direct-response text
- Missing tool objects
- Missing tool names
- Missing argument objects
- Unknown tool-object fields
- Invalid argument structures

A model response is not trusted merely because it is valid JSON.

It must also satisfy the ATLAS decision contract.

---

# Model Provider Integration

The agent communicates through the abstract `ModelProvider` interface.

Normal response method:

```python
def generate_response(
    self,
    user_message: str,
) -> str:
    """Generate a normal response."""
```

Structured response method:

```python
def generate_structured_response(
    self,
    user_message: str,
    schema: dict[str, Any],
) -> str:
    """Generate a schema-constrained response."""
```

This allows the agent to remain provider-independent.

---

## Ollama Integration

The local Ollama provider supports structured decisions using the configured model.

Current structured behavior includes:

- Native JSON-schema output
- Thinking disabled
- Low-temperature generation
- Output-token limits
- Model keep-alive
- Defensive output cleanup

The current recommended development model is:

```text
qwen3:4b
```

Real-model behavior can vary.

Automated tests therefore use scripted providers rather than live Ollama requests.

---

## Reasoning Suppression

The Ollama provider is configured to avoid returning internal reasoning.

The provider should not expose:

```text
<think>
```

or text such as:

```text
Let's reason through this...
```

The output cleaner removes a completed leaked reasoning block when possible.

If reasoning appears without a final answer, the provider raises a model error.

The user should receive only:

- A direct response
- A trusted tool result
- A controlled error

---

# Agent Service

Location:

```text
src/atlas/agent/service.py
```

`AgentService` coordinates the complete agent pipeline.

Responsibilities include:

- Validating user input
- Applying deterministic routing
- Building decision prompts
- Requesting structured model output
- Parsing decisions
- Validating tool requests
- Evaluating permissions
- Executing allowed tools
- Creating pending requests
- Completing approved requests
- Recording denials
- Returning trusted results

The agent service is an orchestration layer.

It should not contain filesystem or tool business logic.

---

# Request Processing

## Direct Response Flow

```text
User Request
    ↓
Agent Prompt Builder
    ↓
Model Structured Decision
    ↓
Decision Parser
    ↓
Decision: respond
    ↓
Return Response
    ↓
Store Conversation Message
```

Example:

```text
You: What is the capital of Poland?

ATLAS: The capital of Poland is Warsaw.
```

---

## Low-Risk Tool Flow

```text
User Request
    ↓
Agent Decision: use_tool
    ↓
Tool Registry Lookup
    ↓
Argument Validation
    ↓
Permission Decision: allow
    ↓
Tool Executor
    ↓
Tool Result
    ↓
Return Trusted Output
```

Example:

```text
You: What is 347 multiplied by 982?

ATLAS: 340754
```

---

## Medium-Risk Tool Flow

```text
User Request
    ↓
Tool Request
    ↓
Argument Validation
    ↓
Permission Decision: confirm
    ↓
Pending Request Stored
    ↓
Return Confirmation Prompt
```

Example:

```text
You: Create a folder called Rocket Design.

ATLAS: Tool create_directory requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

No state change occurs at this stage.

---

## Confirmation Approval Flow

```text
User: confirm yes
    ↓
Retrieve Pending Request
    ↓
Record Approval
    ↓
Execute Saved Tool Request
    ↓
Return Trusted Tool Output
    ↓
Clear Pending State
```

Example:

```text
ATLAS: Created directory: Rocket Design
```

---

## Confirmation Denial Flow

```text
User: confirm no
    ↓
Retrieve Pending Request
    ↓
Record Denial
    ↓
Do Not Execute
    ↓
Clear Pending State
```

Example:

```text
ATLAS: Tool create_directory execution was denied.
```

---

## High-Risk Tool Flow

```text
Tool Request
    ↓
Permission Decision: deny
    ↓
No Execution
    ↓
Return Denial
```

High-risk tools do not reach the executor under the default policy.

---

# Deterministic Safety Routing

Version 1.0.0 includes deterministic routing for recognized file and folder creation requests.

This was added because prompt instructions alone were not sufficient to prevent a local model from falsely claiming that an action had already been completed.

Examples include:

```text
Create a folder called Test Folder.
```

and:

```text
Create a file called hello.txt that says Hello World.
```

These requests are recognized before model decision-making.

---

## Deterministic File Creation

A recognized request such as:

```text
Create a file called hello.txt that says Hello World.
```

is converted into:

```json
{
  "tool_name": "write_text_file",
  "arguments": {
    "path": "hello.txt",
    "content": "Hello World"
  }
}
```

The generated request still passes through:

- Tool lookup
- Argument validation
- Permission evaluation
- Confirmation
- Tool execution
- Filesystem scope enforcement

The deterministic router does not bypass security.

---

## Deterministic Directory Creation

A recognized request such as:

```text
Create a folder called Rocket Design.
```

is converted into:

```json
{
  "tool_name": "create_directory",
  "arguments": {
    "path": "Rocket Design"
  }
}
```

The operation still requires confirmation because `create_directory` is medium risk.

---

## Routing Scope

The current deterministic router is intentionally narrow.

It targets recognized English patterns for:

- File creation
- Directory creation

It does not attempt to function as a complete natural-language parser.

Broad deterministic routing could introduce incorrect interpretation.

New patterns should be added only with:

- Clear user intent
- Narrow matching behavior
- Positive tests
- Negative tests
- Confirmation preservation
- Model-bypass tests
- Argument-cleaning tests

---

# Tool Validation

A model-selected tool request must pass through the registered tool system.

Conceptual validation flow:

```text
Tool Name
    ↓
Registry Lookup
    ↓
Tool Definition
    ↓
Argument Schema Validation
    ↓
Domain-Specific Validation
```

The agent rejects:

- Unregistered tools
- Missing arguments
- Unknown arguments
- Incorrect argument types
- Invalid nested structures
- Unsupported values

A model cannot create a new tool dynamically.

---

# Permission Integration

The agent uses the same permission service as explicit tool commands.

Permission decisions are based on:

- Tool risk level
- Confirmation metadata
- Active permission policy

Current default behavior:

| Tool condition | Decision |
|---|---|
| Low risk without confirmation requirement | Allow |
| Medium risk | Confirm |
| Explicit confirmation requirement | Confirm |
| High risk | Deny |

The model cannot override permission decisions.

A generated tool request does not count as user authorization.

---

# Pending Requests

When a model-selected tool requires confirmation, the agent creates a pending request.

The pending request preserves:

- Tool name
- Tool arguments
- Tool risk level
- Permission evaluation
- Original user message
- Conversation context

Only one tool request may remain pending at a time.

While a request is pending, unrelated user requests are blocked.

Expected response:

```text
A tool request is awaiting confirmation. Use 'confirm yes' or 'confirm no' before submitting another request.
```

Pending requests exist only in process memory.

They are not restored after restarting ATLAS.

---

# Trusted Tool Results

After execution, the agent returns the tool output directly.

Example calculator output:

```text
340754
```

Example directory output:

```text
file: notes.txt (size: 13 bytes)
```

Example write output:

```text
Created file: hello.txt (11 characters)
```

Version 1.0.0 intentionally avoids a second model call after tool execution.

---

## Why the Second Model Call Was Removed

An earlier design sent tool results back to the model to create a natural-language summary.

That caused several problems:

- High latency
- Repeated model requests
- Internal reasoning leakage
- Prompt leakage
- Extremely long final responses
- Truncated responses
- Misrepresentation of successful actions

Returning trusted tool output directly provides:

- Faster responses
- Exact results
- Predictable formatting
- Simpler tests
- Reduced model dependence
- Better security

Future releases may introduce deterministic result formatters.

A second unrestricted model call should not be reintroduced without strong output controls.

---

# Conversation Context

The agent may receive recent conversation history.

Conceptual context:

```text
User: My experimental rocket is named Specter.
Assistant: I will remember the name.
User: What is my experimental rocket named?
```

The context is included in the decision prompt.

The agent does not read the conversation database directly.

`AtlasApp` coordinates with `ConversationService` and provides the resulting context.

Conversation history remains owned by the conversation subsystem.

---

# Persistent Memory Context

Persistent memories may also be included in the model context.

Memory remains separate from conversation history.

Examples:

```text
Memory:
The user's L2 rocket is named Wraith.
```

The agent does not store memories automatically in v1.0.0.

Explicit memory commands remain:

```text
remember <information>
memories
forget <memory ID>
```

Automatic memory creation is planned for a later release.

---

# Explicit Tool Compatibility

The agent does not replace explicit tool commands.

Explicit commands remain supported:

```text
tool calculator {"expression":"15*6"}
```

```text
tool list_directory {"path":"."}
```

```text
tool read_text_file {"path":"notes.txt"}
```

```text
tool create_directory {"path":"Rocket Design"}
```

Explicit and agent-selected requests share:

- Tool registry
- Argument validation
- Permission policy
- Confirmation flow
- Tool executor
- Filesystem service
- Logging

This preserves backward compatibility and provides a deterministic debugging interface.

---

# Agent Examples

## Direct Knowledge Response

```text
You: What is the capital of Poland?

ATLAS: The capital of Poland is Warsaw.
```

---

## Automatic Calculator

```text
You: What is 347 multiplied by 982?

ATLAS: 340754
```

---

## Automatic Workspace Listing

```text
You: What files are in my workspace?

ATLAS:
file: .gitkeep (size: 0 bytes)
file: agent-test.txt (size: 27 bytes)
```

---

## Automatic File Reading

Assume:

```text
workspace/agent-test.txt
```

contains:

```text
Project ATLAS agent test.
```

Request:

```text
You: Read agent-test.txt.
```

Expected result:

```text
ATLAS: Project ATLAS agent test.
```

---

## Directory Creation

```text
You: Create a folder called Test Folder.

ATLAS: Tool create_directory requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

Approve:

```text
You: confirm yes

ATLAS: Created directory: Test Folder
```

---

## File Creation

```text
You: Create a file called hello.txt that says Hello World.

ATLAS: Tool write_text_file requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.
```

Approve:

```text
You: confirm yes

ATLAS: Created file: hello.txt (11 characters)
```

---

## Current Local Time

```text
You: What time is it?

ATLAS:
Current local time

Saturday, August 01, 2026
8:10:48 PM EDT
```

The result is based on the timezone configured on the computer running ATLAS.

---

# Error Handling

Agent failures should produce controlled exceptions.

Examples include:

- Invalid model JSON
- Missing response text
- Missing tool request
- Unknown tool
- Invalid generated arguments
- Tool execution failure
- Empty trusted tool output

Agent errors are logged by the application.

The agent should fail safely rather than attempting to guess or silently continue.

---

## Invalid JSON

Example failure:

```text
The model response was not valid JSON.
```

The parser must not accept arbitrary text as a structured decision.

---

## Hallucinated Tool

If the model selects:

```text
run_shell
```

and the tool is not registered, ATLAS rejects the request.

The tool never reaches permission evaluation or execution.

---

## Invalid Tool Arguments

If the model selects:

```json
{
  "name": "calculator",
  "arguments": {}
}
```

ATLAS rejects the request because `expression` is required.

Invalid arguments should fail before confirmation.

---

## Tool Execution Failure

If an authorized tool fails, the agent raises a controlled agent error.

The underlying cause should be logged.

User-facing error formatting may be improved in future releases to preserve safe filesystem validation details.

---

# Logging

Agent-related logging includes:

- Structured decision request
- User-message length
- Direct-response selection
- Tool selection
- Deterministic routing
- Permission decision
- Pending confirmation
- Confirmation approval
- Confirmation denial
- Tool execution
- Execution duration
- Final response length
- Errors

Logs should not contain:

- Complete prompts
- Full user messages
- Conversation contents
- Memory contents
- File contents
- API keys
- Complete sensitive tool arguments

---

# Testing

Version 1.0.0 includes dedicated agent tests.

Current agent test files:

```text
tests/test_agent_models.py
tests/test_agent_parser.py
tests/test_agent_prompt.py
tests/test_agent_service.py
tests/test_app_agent.py
```

---

## Model Tests

Agent model tests should validate:

- Decision types
- Tool requests
- Pending requests
- Run results
- Invalid states

---

## Parser Tests

Parser tests should validate:

- Direct responses
- Tool decisions
- Invalid JSON
- Non-object JSON
- Missing fields
- Unknown fields
- Invalid decision types
- Invalid response values
- Invalid tool structures

---

## Prompt Tests

Prompt tests should validate:

- System instructions
- Tool catalog
- Parameter schemas
- Risk metadata
- Confirmation metadata
- Conversation context
- Current user request
- Raw JSON requirement
- Workspace behavior
- Calculator behavior
- Current-time behavior
- Filesystem-action behavior

---

## Agent Service Tests

Service tests should validate:

- Direct response
- Low-risk tool execution
- Conversation context
- Empty input rejection
- Unknown-tool rejection
- Invalid-argument rejection
- Medium-risk confirmation
- Approval execution
- Denial behavior
- High-risk denial
- Trusted result behavior

---

## Application Integration Tests

Application-level agent tests should validate:

- Agent availability
- Automatic calculator selection
- Automatic file reading
- Automatic directory listing
- Confirmation workflow
- Pending-request blocking
- Deterministic file creation
- Deterministic directory creation
- Model bypass during deterministic routing
- Conversation-history storage
- Explicit tool compatibility

---

## Running Agent Tests

Run model tests:

```powershell
pytest tests\test_agent_models.py
```

Run parser tests:

```powershell
pytest tests\test_agent_parser.py
```

Run prompt tests:

```powershell
pytest tests\test_agent_prompt.py
```

Run service tests:

```powershell
pytest tests\test_agent_service.py
```

Run application integration tests:

```powershell
pytest tests\test_app_agent.py
```

Run all tests:

```powershell
pytest
```

The v1.0.0 release contains:

```text
204 passing tests
```

unless additional regression tests have intentionally increased the total.

---

# Manual Acceptance Testing

Automated tests do not fully validate real local-model behavior.

Before release, run ATLAS using Ollama:

```powershell
atlas
```

Recommended manual tests:

```text
What is the capital of Poland?
```

```text
What is 347 multiplied by 982?
```

```text
What files are in my workspace?
```

```text
Read agent-test.txt.
```

```text
Create a folder called Test Folder.
```

```text
confirm yes
```

```text
Create a file called hello.txt that says Hello World.
```

```text
confirm yes
```

```text
What time is it?
```

```text
tool calculator {"expression":"15*6"}
```

Confirm:

- Direct responses are concise.
- Tool selection occurs automatically.
- Filesystem reads remain scoped.
- Writes require confirmation.
- No state change occurs before confirmation.
- Denial prevents execution.
- No JSON is exposed.
- No `<think>` text is exposed.
- No prompt text is exposed.
- Current time matches the computer.
- Explicit commands still work.

---

# Security Architecture

The agent is protected by multiple independent layers.

```text
User Request
    ↓
Deterministic Routing
    ↓
Structured Model Decision
    ↓
Decision Parser
    ↓
Registered Tool Lookup
    ↓
Argument Validation
    ↓
Permission Evaluation
    ↓
Confirmation
    ↓
Tool Executor
    ↓
Subsystem Scope Enforcement
```

Security does not depend on model compliance alone.

---

## Security Guarantees

Current guarantees include:

- Only registered tools may execute
- Invalid JSON is rejected
- Unknown fields are rejected
- Unknown tools are rejected
- Invalid arguments are rejected
- Medium-risk actions require confirmation
- High-risk actions are denied
- Pending requests block unrelated actions
- Filesystem paths remain scoped
- Path traversal is rejected
- Read and write limits remain active
- Explicit and agent-selected requests share controls
- Trusted tool output is returned after execution
- No arbitrary shell execution exists
- No autonomous background loop exists

---

## Model Trust Boundary

The model is treated as an untrusted decision generator.

The model may suggest:

- A direct response
- One registered tool
- Structured arguments

The application independently verifies every executable suggestion.

The model cannot:

- Register tools
- Change tool risk levels
- Approve itself
- Bypass confirmation
- Access files directly
- Change allowed directories
- Execute Python code
- Run shell commands
- Modify permission policy
- Execute multiple autonomous steps

---

# Current Limitations

The v1.0.0 agent intentionally does not support:

- Multi-step planning
- Multiple tool calls in one request
- Recursive execution
- Autonomous retries
- Parallel tools
- Persistent plans
- Background tasks
- Scheduled tasks
- Web access
- Code execution
- Desktop control
- Voice
- Vision
- Automatic memory creation
- Automatic conversation titles
- Persistent permission grants
- High-risk approval

Natural-language tool selection depends on model quality.

Deterministic routing currently covers only a limited set of English creation requests.

Trusted tool output may be less conversational than a model-generated summary.

---

# Planned Development

The next planned milestone is:

```text
v1.1.0 — Multi-Step Agent Loop
```

Planned capabilities include:

- Bounded multi-step execution
- Configurable maximum steps
- Tool-result observation
- Replanning
- Sequential tools
- Failure recovery
- Task cancellation
- Repeated confirmations
- Duplicate-action protection
- Final completion summaries
- Agent-loop audit logging

Example future request:

```text
Create a folder called Rockets,
create notes.txt inside it,
and write Project Wraith into the file.
```

Planned execution:

```text
Create Directory
    ↓
Observe Result
    ↓
Write Text File
    ↓
Observe Result
    ↓
Return Completion Summary
```

Every step will still require:

- Registered tools
- Argument validation
- Permission evaluation
- Confirmation where required
- Scoped resource enforcement
- Step limits

---

# Development Rules

When modifying the agent:

1. Keep `AgentService` focused on orchestration.
2. Keep filesystem logic in `FileSystemService`.
3. Keep tool behavior inside tools.
4. Keep authorization inside the permission subsystem.
5. Keep persistence inside memory and conversation services.
6. Parse all structured decisions.
7. Validate all tool arguments.
8. Preserve confirmation requirements.
9. Add regression tests for every bug.
10. Avoid relying on prompt instructions as the only safeguard.
11. Do not expose hidden reasoning.
12. Do not reintroduce an unrestricted second model call after tools.
13. Update this document when behavior changes.
14. Update `ARCHITECTURE.md` when subsystem relationships change.
15. Update `CHANGELOG.md` for each release.

---

# Related Documentation

See:

- [Tool System](tools.md)
- [Permission System](permissions.md)
- [Secure Filesystem](filesystem.md)
- [Configuration](configuration.md)
- [Development Guide](development.md)
- [Project Architecture](../ARCHITECTURE.md)
- [Roadmap](../ROADMAP.md)
- [Changelog](../CHANGELOG.md)

---

# Summary

Project ATLAS v1.0.0 introduces a constrained, tool-using agent architecture.

The agent can:

- Interpret natural-language requests
- Respond directly
- Select one registered tool
- Generate structured arguments
- Pass through validation
- Pass through permission policy
- Pause for confirmation
- Execute approved tools
- Return trusted results
- Use conversation context
- Preserve explicit command compatibility

The agent cannot bypass the existing safety architecture.

Every executable request remains subject to:

- Tool registration
- Schema validation
- Permission evaluation
- Confirmation
- Tool execution controls
- Filesystem scope enforcement
- Structured logging
- Regression testing

This foundation establishes the architecture for future multi-step planning, web research, semantic memory, code execution, desktop automation, voice, vision, and robotics without granting unrestricted autonomy in the first agent release.

---

**Document Version:** ATLAS v1.0.0

**Status:** Current

**Last Updated:** August 2026