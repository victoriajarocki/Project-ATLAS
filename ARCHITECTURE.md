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
- Permissions
- Logging
- Tools
- Voice
- Vision
- Planning

Subsystems communicate through stable interfaces rather than direct implementation dependencies whenever practical.

This allows components to evolve independently while minimizing breaking changes.

---

## 2. Local-First

Whenever practical, user information should remain on the local machine.

Current examples include:

- SQLite memory database
- Conversation database
- Ollama local inference
- Local log files

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

Future cloud integrations should require explicit user authorization.

---

## 4. Extensibility

New capabilities should primarily be added through new modules rather than modifying existing implementations.

The architecture should support:

- Additional AI providers
- New tools
- New memory systems
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
```

All major operations are observed through the structured logging subsystem.

ATLAS Core is responsible for coordinating the interactions between subsystems.

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
├── src/
│   └── atlas/
│       ├── config/
│       ├── conversations/
│       ├── core/
│       ├── memory/
│       ├── models/
│       ├── observability/
│       ├── permissions/
│       ├── security/
│       └── tools/
│
├── tests/
│
├── docs/
│
├── README.md
├── CHANGELOG.md
├── ROADMAP.md
├── ARCHITECTURE.md
├── pyproject.toml
└── .env.example
```

The repository is organized around major architectural subsystems rather than implementation layers.

Each subsystem owns its own:

- Models
- Services
- Database interfaces
- Validation
- Tests

This keeps responsibilities localized and makes large-scale expansion significantly easier.

---

# Subsystem Overview

# Configuration

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

The configuration subsystem is intentionally isolated from application logic.

Every subsystem receives configuration through dependency injection rather than reading environment variables directly.

This improves testing, portability, and future deployment flexibility.

---

# Core

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

ATLAS Core intentionally contains very little business logic.

Instead, it orchestrates specialized subsystems.

Current responsibilities include:

- Processing normal AI conversations
- Processing built-in commands
- Processing tool requests
- Permission evaluation
- Pending confirmation state
- Tool execution
- Conversation persistence
- Memory persistence

Future versions will expand the Core into a lightweight orchestration engine while keeping individual subsystem logic separate.

---

# Models

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

Future providers:

- Anthropic
- Google Gemini
- LM Studio
- vLLM
- Azure OpenAI
- Local custom inference servers

The Core communicates only through the abstract `ModelProvider` interface.

This allows providers to be swapped without changing application logic.

---

# Memory

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

# Conversations

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

# Observability

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

Logging is designed for both debugging and operational diagnostics.

Sensitive information should never appear in log files.

Future observability work includes:

- Performance metrics
- Health checks
- Telemetry dashboard
- Distributed tracing
- Runtime statistics

---

# Permissions

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

- PermissionDecision
- PermissionEvaluation
- PendingToolRequest
- PermissionPolicy
- PermissionService

Permission decisions:

```text
allow
confirm
deny
```

Default policy:

| Tool Condition | Decision |
|----------------|----------|
| Low risk without confirmation | Allow |
| Medium risk | Confirm |
| Explicit confirmation required | Confirm |
| High risk | Deny |

The permission subsystem never executes tools.

Instead, it determines whether execution is permitted.

ATLAS Core currently owns the temporary pending confirmation state and resolves:

```text
confirm yes
confirm no
```

Future capabilities include:

- Session permissions
- Persistent approvals
- User authentication
- Role-based access
- Trusted directories
- Hardware safety controls
- Remote authorization

---

# Tool Framework

Location:

```text
src/atlas/tools
```

Responsibilities:

- Define the common Tool interface
- Register available tools
- Describe tool metadata
- Validate arguments
- Execute authorized tools
- Return structured results

Current components:

- Tool
- ToolDefinition
- ToolRegistry
- ToolExecutor
- ToolResult
- ToolRiskLevel

Current built-in tools:

- Calculator
- Current Time
- Confirmation Demo

Tools declare:

- Risk level
- Parameter schema
- Confirmation requirement

The tool framework does **not** decide whether a tool is allowed to execute.

Authorization belongs exclusively to the permission subsystem.

Future built-in tools include:

- File tools
- Browser tools
- Engineering tools
- Calendar integrations
- GitHub integrations
- Robotics interfaces

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
Validate JSON
  ↓
Tool Registry
  ↓
Retrieve Tool Definition
  ↓
Permission Service
  ↓
Permission Policy
  ↓
Allow / Confirm / Deny
  ↓
Tool Executor
  ↓
Tool Result
  ↓
User
```

Important rules:

- Invalid JSON never reaches the executor.
- Unknown tools never reach permission evaluation.
- Denied tools never reach execution.
- Confirmation-controlled tools remain pending until explicitly approved.
- Approved requests execute exactly once.
- Pending requests are cleared after approval or denial.

The permission system forms the security boundary between tool requests and tool execution.

---

# Dependency Direction

Dependencies should point toward stable interfaces rather than concrete implementations.

Current dependency direction:

```text
ATLAS Core
    ↓
Permission Service
    ↓
Permission Policy
    ↓
Tool Executor
    ↓
Registered Tool
```

Subsystems should avoid unnecessary cross-dependencies.

For example, this is discouraged:

```text
Memory
   ↓
Models
   ↓
Tools
```

Instead, coordination should occur through ATLAS Core.

Tools declare their own metadata but must never authorize themselves.

Authorization belongs to the permission subsystem.

---

# Data Storage Architecture

Project ATLAS separates long-term storage into multiple independent persistence layers.

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

Current persisted information:

- Long-term memories
- Conversation metadata
- Conversation messages

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

Current exception categories include:

- Configuration errors
- Model errors
- Memory errors
- Conversation errors
- Tool errors
- Permission errors

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

├── test_models.py
├── test_memory.py
├── test_conversations.py
├── test_tools.py
├── test_permissions.py
└── test_app.py
```

Testing philosophy:

- Unit tests validate individual components.
- Integration tests validate subsystem interaction.
- Core tests validate orchestration.
- Every bug should eventually receive a regression test.

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
- Errors

Future logging additions:

- Performance metrics
- Memory statistics
- Model latency
- Tool latency
- Resource usage
- Hardware telemetry

Logs should help developers understand system behavior without exposing private user information.

---

# Security Architecture

Security is implemented in layers.

Current layers:

```text
User
   ↓
Input Validation
   ↓
Command Parsing
   ↓
Permission Evaluation
   ↓
Authorized Tool Execution
   ↓
Structured Logging
```

Principles:

- Validation before execution
- Least privilege
- Explicit authorization
- Safe defaults
- Deny by default for high-risk actions
- Audit significant operations

Future work includes:

- Authentication
- Role-based authorization
- Trusted devices
- Encrypted storage
- Secure secrets management
- Hardware safety controls

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
              Permission System
                     │
        ┌────────────┼────────────┐
        │            │            │
   Local Tools   Remote APIs   Hardware
        │            │            │
        └────────────┴────────────┘
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

Authorization should occur before execution.

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
- Assisting with engineering workflows
- Understanding documents
- Speaking naturally
- Seeing through cameras and screenshots
- Coordinating multiple devices
- Operating dedicated hardware
- Supporting robotics

Every release should strengthen the underlying architecture rather than increasing complexity.

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
Permission System
        │
        ▼
Tool Framework
        │
        ▼
Infrastructure
        │
        ▼
Persistence
```

Each layer has a clearly defined responsibility.

Higher layers coordinate behavior.

Lower layers provide reusable capabilities.

Maintaining this separation allows Project ATLAS to evolve from a command-line AI assistant into a secure, voice-first, multi-device AI operating platform without requiring major architectural redesigns.

---

**Document Version:** ATLAS v0.8.0
**Status:** Current Architecture
**Last Updated:** August 2026