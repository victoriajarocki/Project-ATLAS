# Project ATLAS Architecture

---

# Purpose

This document describes the high-level software architecture of Project ATLAS.

Unlike implementation documentation, this document focuses on the organization of the system, the responsibilities of each subsystem, the relationships between those subsystems, and the engineering principles that guide long-term development.

Project ATLAS is intentionally designed as an extensible AI operating system rather than a traditional chatbot. Every major capability is implemented as an independent subsystem with well-defined interfaces so future functionality can be added without redesigning the existing codebase.

This document should remain relatively stable across releases. Individual implementation details belong in subsystem documentation, while this document explains how the major pieces fit together.

---

# Design Philosophy

Project ATLAS is built around six fundamental architectural principles.

## 1. Modularity

Every subsystem should solve one problem well.

Examples include:

- AI Models
- Memory
- Conversations
- Observability
- Permissions
- Filesystem
- Tools
- Voice
- Vision
- Planning

Subsystems communicate through stable interfaces rather than direct implementation dependencies whenever practical.

This allows components to evolve independently while minimizing breaking changes.

---

## 2. Local-First

Whenever practical, user information and execution should remain on the local machine.

Current examples include:

- SQLite memory database
- SQLite conversation database
- Ollama local inference
- Local log files
- Scoped local filesystem access

Cloud providers remain optional rather than mandatory.

---

## 3. Privacy

Sensitive information should never leave the user's computer unless explicitly requested.

Examples include:

- Environment variables
- API keys
- Memory database
- Conversation history
- Log files
- Local documents
- Filesystem workspace contents

Future cloud integrations should require explicit user authorization.

---

## 4. Extensibility

New capabilities should primarily be added through new modules rather than modifying existing implementations.

The architecture should support:

- Additional AI providers
- New tools
- New memory systems
- New filesystem capabilities
- Desktop interfaces
- Voice interfaces
- Vision systems
- Robotics hardware

without requiring major redesigns.

---

## 5. Reliability

Every subsystem should be:

- Typed
- Tested
- Logged
- Documented
- Independently maintainable

Failures should produce explicit, actionable errors rather than silent failures.

---

## 6. Long-Term Stability

Project ATLAS is intended to evolve over many years.

Architectural decisions prioritize maintainability, safety, and extensibility over short-term convenience.

Breaking changes should be rare and deliberate.

---

# High-Level Architecture

Current system overview:

```text
                    User
                      │
                      ▼
              Command-Line Interface
                      │
                      ▼
                  ATLAS Core
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
 Models            Memory        Conversations
    │                 │                 │
    └─────────────────┴─────────────────┘
                      │
                      ▼
               Tool Registry
                      │
                      ▼
          Shared Argument Validation
                      │
                      ▼
             Permission Service
                      │
                      ▼
              Permission Policy
                      │
         ┌────────────┼────────────┐
         │            │            │
       Allow       Confirm       Deny
         │            │            │
         │       User decision     │
         │            │            │
         └────────────┴────────────┘
                      │
                      ▼
                Tool Executor
                      │
                      ▼
                Tool Modules
                      │
                      ▼
          Filesystem Service Layer
                      │
                      ▼
             Scoped Path Resolver
                      │
                      ▼
         Configured Allowed Directory
```

All major operations are observed through the structured logging subsystem.

ATLAS Core is responsible for coordinating interactions between subsystems.

Individual subsystems should not directly coordinate unrelated subsystems.

Instead, communication should follow the pattern:

```text
Subsystem
    ↓
ATLAS Core
    ↓
Another Subsystem
```

This minimizes coupling while making future refactoring significantly easier.

---

# Repository Structure

```text
Project-ATLAS/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── configuration.md
│   ├── development.md
│   ├── filesystem.md
│   ├── installation.md
│   ├── permissions.md
│   └── tools.md
│
├── src/
│   └── atlas/
│       ├── config/
│       ├── conversations/
│       ├── core/
│       ├── filesystem/
│       ├── memory/
│       ├── models/
│       ├── observability/
│       ├── permissions/
│       └── tools/
│
├── tests/
│   ├── test_app.py
│   ├── test_conversations.py
│   ├── test_filesystem.py
│   ├── test_main.py
│   ├── test_memory.py
│   ├── test_models.py
│   ├── test_observability.py
│   ├── test_permissions.py
│   ├── test_tool_validation.py
│   └── test_tools.py
│
├── workspace/
│   └── .gitkeep
│
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── README.md
└── ROADMAP.md
```

The repository is organized around major architectural subsystems rather than implementation layers.

Each subsystem owns its own:

- Models
- Services
- Validation
- Exceptions
- Tests
- Documentation

This keeps responsibilities localized and makes large-scale expansion significantly easier.

---

# Subsystem Overview

## Configuration

Location:

```text
src/atlas/config
```

Responsibilities:

- Load application settings
- Read environment variables
- Validate configuration
- Provide strongly typed settings
- Centralize runtime configuration
- Configure filesystem boundaries and size limits

Current filesystem settings include:

```text
ATLAS_ALLOWED_DIRECTORIES
ATLAS_FILESYSTEM_MAX_READ_BYTES
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS
```

The configuration subsystem is intentionally isolated from application logic.

Every subsystem receives configuration through dependency injection rather than reading environment variables directly.

This improves testing, portability, and future deployment flexibility.

---

## Core

Location:

```text
src/atlas/core
```

Responsibilities:

- Coordinate all subsystems
- Receive user requests
- Route commands
- Manage application lifecycle
- Build model context
- Coordinate conversations
- Coordinate memory
- Coordinate permissions
- Coordinate tools
- Enforce validation before authorization

ATLAS Core intentionally contains very little subsystem-specific business logic.

Instead, it orchestrates specialized services.

Current responsibilities include:

- Processing normal AI conversations
- Processing built-in commands
- Processing tool requests
- Parsing tool arguments
- Triggering shared argument validation
- Permission evaluation
- Pending confirmation state
- Tool execution
- Conversation persistence
- Memory persistence

Future versions will expand the Core into a lightweight orchestration engine while keeping individual subsystem logic separate.

---

## Models

Location:

```text
src/atlas/models
```

Responsibilities:

- Abstract AI providers
- Model selection
- Provider configuration
- Provider-specific adapters
- Error normalization

Current providers:

- Mock Provider
- OpenAI Provider
- Ollama Provider

Future providers may include:

- Anthropic
- Google Gemini
- LM Studio
- vLLM
- Azure OpenAI
- Local custom inference servers

The Core communicates only through the abstract `ModelProvider` interface.

This allows providers to be swapped without changing application logic.

---

## Memory

Location:

```text
src/atlas/memory
```

Responsibilities:

- Persistent memory storage
- Memory validation
- Memory retrieval
- Context generation
- Memory deletion
- Memory categorization

Current implementation:

- SQLite
- Source tracking
- Categories
- Timestamps
- Memory IDs

Memory is intentionally separated from conversations.

Memory represents long-term knowledge.

Conversations represent dialogue history.

Future versions will introduce semantic retrieval using embeddings.

---

## Conversations

Location:

```text
src/atlas/conversations
```

Responsibilities:

- Persistent conversation storage
- Chat creation
- Chat switching
- Conversation history
- Context generation
- Conversation metadata

Current implementation:

- SQLite
- Conversation IDs
- Titles
- Message history

Future work includes:

- Automatic summaries
- Search
- Conversation archiving
- Semantic retrieval
- Token-aware history compression

---

## Observability

Location:

```text
src/atlas/observability
```

Responsibilities:

- Structured logging
- Request timing
- Request IDs
- Rotating log files
- Error reporting
- Startup logging
- Shutdown logging
- Tool and permission audit records

Logging is designed for both debugging and operational diagnostics.

Sensitive information should never appear in log files.

Filesystem logs may include:

- Resolved operation type
- File or directory path
- File size
- Character count
- Tool result
- Execution duration

Filesystem logs must not include complete file contents.

Future observability work includes:

- Performance metrics
- Health checks
- Telemetry dashboard
- Distributed tracing
- Runtime statistics

---

## Permissions

Location:

```text
src/atlas/permissions
```

Responsibilities:

- Evaluate tool authorization
- Interpret tool risk levels
- Require explicit user confirmation
- Deny prohibited actions
- Record permission decisions
- Protect the boundary between tool requests and execution

Current components:

- `PermissionDecision`
- `PermissionEvaluation`
- `PendingToolRequest`
- `PermissionPolicy`
- `PermissionService`

Permission decisions:

```text
allow
confirm
deny
```

Default policy:

| Tool condition | Decision |
|---|---|
| Low risk without confirmation | Allow |
| Medium risk | Confirm |
| Explicit confirmation required | Confirm |
| High risk | Deny |

The permission subsystem never executes tools.

Instead, it determines whether execution is permitted.

ATLAS Core currently owns temporary pending-confirmation state and resolves:

```text
confirm yes
confirm no
```

Filesystem policy examples:

| Tool | Risk | Behavior |
|---|---|---|
| `list_directory` | Low | Execute immediately |
| `file_info` | Low | Execute immediately |
| `read_text_file` | Low | Execute immediately |
| `create_directory` | Medium | Require confirmation |
| `write_text_file` | Medium | Require confirmation |

Future capabilities include:

- Session permissions
- Persistent approvals
- User authentication
- Role-based access
- Trusted directories
- Hardware safety controls
- Remote authorization

---

## Filesystem

Location:

```text
src/atlas/filesystem
```

Responsibilities:

- Restrict filesystem access to configured directories
- Resolve user-supplied paths safely
- Prevent path traversal
- Read UTF-8 text files
- Write UTF-8 text files
- Create directories
- List directory contents
- Inspect file and directory metadata
- Enforce read and write limits
- Normalize filesystem errors

Current components:

- `ScopedPathResolver`
- `FileSystemService`
- `FileSystemEntry`
- `FileSystemEntryType`
- `FileReadResult`
- `FileWriteResult`
- Filesystem-specific exceptions

The filesystem subsystem does not own permission decisions.

Its responsibility is to ensure that an already-authorized operation remains confined to an approved filesystem scope.

### Scoped Path Resolver

`ScopedPathResolver` converts a user path into a resolved absolute path and verifies that it remains inside at least one configured root.

Conceptual flow:

```text
User path
   ↓
Trim and normalize
   ↓
Resolve relative or absolute location
   ↓
Canonicalize path
   ↓
Compare against allowed roots
   ↓
Allow or reject
```

Relative paths resolve against the first configured allowed directory.

Absolute paths are accepted only when they remain inside an allowed root.

Path traversal such as:

```text
../outside.txt
```

is rejected after canonical resolution.

### FileSystemService

`FileSystemService` provides the filesystem operations used by built-in tools.

Current operations:

- `list_directory`
- `get_info`
- `read_text_file`
- `create_directory`
- `write_text_file`

The service enforces:

- Existing-path checks
- File-versus-directory checks
- UTF-8 decoding
- Maximum read size
- Maximum write size
- Explicit overwrite behavior
- Scoped path resolution

### Filesystem Models

`FileSystemEntry` describes visible files and directories.

It includes:

- Entry name
- Resolved path
- Entry type
- File size when applicable
- Last-modified timestamp

`FileReadResult` includes:

- Resolved path
- File content
- Character count

`FileWriteResult` includes:

- Resolved path
- Character count
- Whether the file was newly created

### Workspace Sandbox

The default workspace is:

```text
workspace/
```

The directory is retained in Git through:

```text
workspace/.gitkeep
```

Workspace contents are excluded through `.gitignore`.

The default configuration is:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Multiple directories may be configured using semicolon-separated values.

---

## Tool Framework

Location:

```text
src/atlas/tools
```

Responsibilities:

- Define the common `Tool` interface
- Register available tools
- Describe tool metadata
- Validate arguments
- Execute authorized tools
- Return structured results

Current components:

- `Tool`
- `ToolDefinition`
- `ToolRegistry`
- `ToolExecutor`
- `ToolResult`
- `ToolRiskLevel`
- Shared argument validator

Current built-in tools:

- Calculator
- Current Time
- Confirmation Demo
- List Directory
- File Information
- Read Text File
- Create Directory
- Write Text File

Tools declare:

- Risk level
- Parameter schema
- Confirmation requirement

The tool framework does not decide whether a tool is allowed to execute.

Authorization belongs to the permission subsystem.

### Shared Argument Validation

Location:

```text
src/atlas/tools/validation.py
```

The shared validator enforces supported JSON-schema fields before permission evaluation and again before execution.

Current validation includes:

- Root object schema
- Required arguments
- Unknown arguments
- String values
- Boolean values
- Integer values
- Number values
- Object values
- Array values
- Null values
- Enum values
- Nested object schemas
- Array item schemas

This avoids duplicating basic schema validation inside every tool.

Individual tools remain responsible for domain-specific validation.

Examples include:

- Arithmetic syntax restrictions
- Filesystem path scope
- UTF-8 requirements
- File size limits
- Existing-file overwrite behavior

---

# Request Processing Flow

Every user request passes through ATLAS Core.

Normal conversation follows:

```text
User
  ↓
Command-Line Interface
  ↓
ATLAS Core
  ↓
Memory Context
  ↓
Conversation Context
  ↓
Model Provider
  ↓
Assistant Response
  ↓
Conversation Storage
```

Tool execution follows:

```text
User
  ↓
ATLAS Core
  ↓
Parse Command
  ↓
Decode JSON
  ↓
Require JSON Object
  ↓
Tool Registry
  ↓
Retrieve Tool Definition
  ↓
Shared Argument Validation
  ↓
Permission Service
  ↓
Permission Policy
  ↓
Allow / Confirm / Deny
  ↓
Tool Executor
  ↓
Defense-in-Depth Validation
  ↓
Tool Implementation
  ↓
Tool Result
  ↓
User
```

Important rules:

- Invalid JSON never reaches the registry.
- Non-object arguments are rejected.
- Unknown tools never reach permission evaluation.
- Invalid arguments never enter the confirmation workflow.
- Denied tools never reach execution.
- Confirmation-controlled tools remain pending until explicitly approved.
- Approved requests execute exactly once.
- Pending requests are cleared after approval or denial.
- The executor validates arguments again immediately before execution.

The permission system forms the authorization boundary between a valid tool request and tool execution.

---

# Filesystem Tool Flow

Read-only filesystem operations follow:

```text
User
  ↓
ATLAS Core
  ↓
Shared Argument Validation
  ↓
Permission Decision: Allow
  ↓
Tool Executor
  ↓
Filesystem Tool
  ↓
FileSystemService
  ↓
ScopedPathResolver
  ↓
Allowed Workspace
  ↓
Result
```

State-changing filesystem operations follow:

```text
User
  ↓
ATLAS Core
  ↓
Shared Argument Validation
  ↓
Permission Decision: Confirm
  ↓
Pending Request
  ↓
User enters confirm yes or confirm no
  ↓
Approval or Denial
  ↓
Tool Executor
  ↓
Filesystem Tool
  ↓
FileSystemService
  ↓
ScopedPathResolver
  ↓
Allowed Workspace
```

A write or directory-creation request cannot modify the filesystem before explicit approval.

---

# Dependency Direction

Dependencies should point toward stable interfaces rather than concrete implementations.

Current tool and filesystem dependency direction:

```text
ATLAS Core
    ↓
Tool Registry
    ↓
Shared Argument Validator
    ↓
Permission Service
    ↓
Permission Policy
    ↓
Tool Executor
    ↓
Filesystem Tool
    ↓
FileSystemService
    ↓
ScopedPathResolver
```

Subsystems should avoid unnecessary cross-dependencies.

For example, this is discouraged:

```text
Memory
   ↓
Models
   ↓
Filesystem
```

Instead, coordination should occur through ATLAS Core or another dedicated orchestration service.

Tools declare their metadata but must never authorize themselves.

Authorization belongs to the permission subsystem.

Filesystem scope enforcement belongs to the filesystem subsystem.

---

# Data Storage Architecture

Project ATLAS separates long-term storage into independent persistence layers.

Current storage architecture:

```text
                SQLite Database
                      │
      ┌───────────────┴───────────────┐
      │                               │
 Persistent Memory             Conversations
      │                               │
 Memory Service            Conversation Service
      │                               │
      └───────────────┬───────────────┘
                      │
                  ATLAS Core
```

The local filesystem workspace is separate from SQLite persistence:

```text
Configured Workspace
        │
ScopedPathResolver
        │
FileSystemService
        │
Filesystem Tools
        │
ATLAS Core
```

Current persisted information:

- Long-term memories
- Conversation metadata
- Conversation messages
- User-approved workspace files and directories

Current non-persistent information:

- Pending confirmation requests
- Active model provider
- Runtime configuration
- Current request state

Future storage layers may include:

- Vector databases
- File indexes
- Document indexes
- User preferences
- Permission policies
- Planning history
- Robotics state

Keeping storage responsibilities isolated allows individual persistence mechanisms to evolve independently.

---

# Error Handling Philosophy

Every subsystem should fail safely.

General rules:

- Invalid input should produce validation errors.
- Internal failures should produce descriptive exceptions.
- Failures should be logged.
- Sensitive information should never appear in exception messages.
- Partial failures should not corrupt persistent state.
- Invalid operations should not reach permission or execution unnecessarily.

Current exception categories include:

- Configuration errors
- Model errors
- Memory errors
- Conversation errors
- Tool errors
- Permission errors
- Filesystem errors

Filesystem exception hierarchy includes:

- `FileSystemError`
- `FileSystemValidationError`
- `PathOutsideAllowedScopeError`
- `FileSystemOperationError`

Future releases may introduce:

- Recovery strategies
- Retry policies
- Fault isolation
- Background error reporting

---

# Testing Architecture

Testing is organized by subsystem.

```text
tests/
├── test_app.py
├── test_conversations.py
├── test_filesystem.py
├── test_main.py
├── test_memory.py
├── test_models.py
├── test_observability.py
├── test_permissions.py
├── test_tool_validation.py
└── test_tools.py
```

Current test coverage includes:

- Model provider behavior
- Memory persistence
- Conversation persistence
- Structured logging
- Permission decisions
- Confirmation workflows
- Tool registration
- Shared schema validation
- Filesystem path scope
- Filesystem service behavior
- Filesystem tool integration
- Core orchestration

Testing philosophy:

- Unit tests validate individual components.
- Integration tests validate subsystem interaction.
- Core tests validate orchestration.
- Security boundaries require explicit regression tests.
- Every bug should eventually receive a regression test.

Current v0.9.0 test suite:

```text
131 passing tests
```

Future testing additions include:

- Performance tests
- Load tests
- Long-running memory tests
- Tool stress testing
- Voice-interface tests
- Robotics simulation tests

---

# Logging Architecture

Every significant operation should be observable.

Current logging includes:

- Startup
- Shutdown
- Request IDs
- Request timing
- Memory operations
- Conversation operations
- Tool execution
- Permission decisions
- Filesystem operations
- Errors

Future logging additions:

- Performance metrics
- Memory statistics
- Model latency
- Tool latency
- Resource usage
- Hardware telemetry

Logs should help developers understand system behavior without exposing private user information.

Complete user messages, complete file contents, credentials, and secrets must not be written to logs.

---

# Security Architecture

Security is implemented in layers.

Current layers:

```text
User
   ↓
Command Parsing
   ↓
JSON Decoding
   ↓
Shared Argument Validation
   ↓
Permission Evaluation
   ↓
Authorized Tool Execution
   ↓
Filesystem Scope Enforcement
   ↓
Structured Logging
```

Principles:

- Validation before authorization
- Authorization before execution
- Scope enforcement inside the target subsystem
- Least privilege
- Explicit authorization
- Safe defaults
- Deny by default for high-risk actions
- Audit significant operations
- Defense-in-depth validation

Filesystem-specific protections include:

- Configured allowed roots
- Canonical path resolution
- Parent-traversal rejection
- Absolute-path scope checks
- UTF-8-only reads
- Read-size limits
- Write-size limits
- Existing-file overwrite protection
- Confirmation for state-changing operations
- No deletion support in v0.9.0
- No unrestricted shell execution

Future work includes:

- Authentication
- Role-based authorization
- Trusted devices
- Encrypted storage
- Secure secrets management
- Persistent scoped grants
- Hardware safety controls

---

# Current Limitations

ATLAS v0.9.0 intentionally limits filesystem functionality.

Current limitations include:

- Text files must be valid UTF-8
- Binary file reading is not supported
- File deletion is not supported
- File renaming is not supported
- File moving is not supported
- File copying is not supported
- Symbolic-link management is not exposed
- Only configured directories are accessible
- Persistent permission grants are not supported
- Tool selection still requires explicit CLI commands

These limitations keep the first filesystem release narrow, testable, and secure.

---

# Future Architecture

As Project ATLAS evolves, additional subsystems will be introduced.

Planned architecture:

```text
                          User
                            │
      ┌─────────────────────┼─────────────────────┐
      │                     │                     │
 Desktop UI            Voice Interface       Remote Client
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            │
                       ATLAS Core
                            │
 ┌─────────┬─────────┬─────────┬─────────┬─────────┐
 │         │         │         │         │         │
Models   Memory  Conversations Vision  Planning  Knowledge
 │         │         │         │         │         │
 └───────────────────┼────────────────────────────────────┘
                     │
              Tool Registry
                     │
          Shared Validation Layer
                     │
              Permission System
                     │
        ┌────────────┼────────────┐
        │            │            │
   Local Tools   Remote APIs   Hardware
        │            │            │
        └────────────┴────────────┘
                     │
          Scoped Resource Services
                     │
           Logging & Observability
```

This architecture intentionally allows future interfaces and capabilities to be added without redesigning the existing core.

---

# Scalability

Project ATLAS is designed to scale in multiple dimensions.

Current scalability goals include:

- Additional AI providers
- Larger memory stores
- More conversations
- Larger tool libraries
- Multiple allowed filesystem roots

Future scalability goals include:

- Multiple concurrent users
- Distributed inference
- Network services
- Multi-device synchronization
- Raspberry Pi clients
- Dedicated ATLAS hardware
- Robotics integration

Subsystem isolation minimizes the impact of future expansion.

---

# Engineering Principles

Every subsystem should follow these principles.

## Single Responsibility

Each subsystem should solve one primary problem.

## Stable Interfaces

Public interfaces should change infrequently.

## Strong Typing

Use explicit typing throughout the project.

## Dependency Injection

Subsystems should receive dependencies rather than creating them internally whenever practical.

## Testability

Every subsystem should be independently testable.

## Documentation

Every subsystem should be documented before significant expansion.

## Observability

Operations should be visible through structured logging.

## Security

Validation and authorization should occur before execution.

## Defense in Depth

Critical boundaries should be checked at more than one layer.

## Extensibility

New functionality should primarily be added through new modules instead of modifying unrelated code.

---

# Long-Term Vision

Project ATLAS is not intended to become a single AI model.

It is intended to become a complete personal AI operating platform capable of:

- Running local or cloud AI models
- Maintaining reliable long-term memory
- Managing conversations
- Safely executing tools
- Interacting with scoped local files
- Assisting with engineering workflows
- Understanding documents
- Speaking naturally
- Seeing through cameras and screenshots
- Coordinating multiple devices
- Operating dedicated hardware
- Supporting robotics

Every release should strengthen the underlying architecture rather than increasing unnecessary complexity.

---

# Architecture Summary

The architecture of Project ATLAS is intentionally layered.

```text
User Interfaces
        │
        ▼
   ATLAS Core
        │
        ▼
Application Services
        │
        ▼
Shared Validation
        │
        ▼
Permission System
        │
        ▼
Tool Framework
        │
        ▼
Scoped Resource Services
        │
        ▼
Infrastructure and Persistence
```

Each layer has a clearly defined responsibility.

Higher layers coordinate behavior.

Lower layers provide reusable capabilities and enforce local safety boundaries.

Maintaining this separation allows Project ATLAS to evolve from a command-line AI assistant into a secure, agent-driven, voice-first, multi-device AI operating platform without requiring major architectural redesigns.

---

**Document Version:** ATLAS v0.9.0
**Status:** Current Architecture
**Last Updated:** August 2026
