# Project ATLAS Architecture

---

# Purpose

This document describes the high-level software architecture of Project ATLAS.

Unlike implementation documentation, this document focuses on the organization of the system, the responsibilities of each subsystem, the relationships between those subsystems, and the engineering principles that guide long-term development.

Project ATLAS is intentionally designed as a modular, local-first AI operating system rather than a traditional chatbot. Every major capability is implemented as an independent subsystem with stable interfaces so future functionality can be added without redesigning the existing codebase.

Version 1.0.0 introduces the first ATLAS agent architecture. The system can now interpret natural-language requests, determine whether a registered tool is required, execute authorized tools, and safely return trusted results while preserving strict security boundaries.

This document should remain relatively stable across releases. Individual implementation details belong in subsystem documentation, while this document explains how the major architectural pieces fit together.

---

# Design Philosophy

Project ATLAS is built around seven fundamental architectural principles.

## 1. Modularity

Every subsystem should solve one problem well.

Current subsystems include:

- Agent
- AI Models
- Memory
- Conversations
- Observability
- Permissions
- Filesystem
- Tools

Future subsystems include:

- Planning
- Voice
- Vision
- Desktop Automation
- Robotics

Subsystems communicate through stable interfaces rather than direct implementation dependencies whenever practical.

This allows components to evolve independently while minimizing breaking changes.

---

## 2. Local-First

Whenever practical, user information and execution should remain on the local machine.

Current local capabilities include:

- SQLite memory database
- SQLite conversation database
- Ollama local inference
- Local log files
- Scoped local filesystem access
- Local permission enforcement
- Local agent orchestration

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

## 4. Security by Design

Safety is enforced through layered validation.

Current security layers include:

- Structured agent decisions
- Tool-name validation
- Tool-argument validation
- Permission evaluation
- Confirmation workflow
- Scoped filesystem enforcement
- Defense-in-depth validation
- Structured logging

No subsystem may bypass these boundaries.

---

## 5. Extensibility

New capabilities should primarily be added through new modules rather than modifying existing implementations.

The architecture supports:

- Additional AI providers
- New agent capabilities
- New tools
- New memory systems
- New filesystem capabilities
- Desktop interfaces
- Voice interfaces
- Vision systems
- Robotics hardware

without requiring major redesigns.

---

## 6. Reliability

Every subsystem should be:

- Typed
- Tested
- Logged
- Documented
- Independently maintainable

Failures should produce explicit, actionable errors rather than silent failures.

---

## 7. Long-Term Stability

Project ATLAS is intended to evolve over many years.

Architectural decisions prioritize maintainability, safety, modularity, and extensibility over short-term convenience.

Breaking changes should remain rare and deliberate.

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
                       AtlasApp
                           │
          ┌────────────────┴────────────────┐
          │                                 │
     Command Router                  Agent Service
          │                                 │
          │                    Structured Prompt Builder
          │                                 │
          │                           Model Provider
          │                                 │
          │                    Structured Decision Parser
          │                                 │
          └────────────────┬────────────────┘
                           │
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
          ┌────────────────┼────────────────┐
          │                │                │
        Allow           Confirm          Deny
          │                │                │
          │         User Confirmation       │
          │                │                │
          └────────────────┴────────────────┘
                           │
                           ▼
                     Tool Executor
                           │
                           ▼
                    Built-in Tools
                           │
                           ▼
                 Filesystem Service
                           │
                           ▼
                 Scoped Path Resolver
                           │
                           ▼
              Configured Allowed Directory
```

All major operations are observed through the structured logging subsystem.

AtlasApp coordinates interactions between every subsystem.

Individual subsystems should never directly coordinate unrelated subsystems.

Instead, communication follows the pattern:

```text
Subsystem
    ↓
AtlasApp
    ↓
Another Subsystem
```

This minimizes coupling while making future architectural changes significantly easier.

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
│   ├── agent.md
│   ├── configuration.md
│   ├── development.md
│   ├── filesystem.md
│   ├── installation.md
│   ├── permissions.md
│   └── tools.md
│
├── src/
│   └── atlas/
│       ├── agent/
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
│   ├── test_agent_models.py
│   ├── test_agent_parser.py
│   ├── test_agent_prompt.py
│   ├── test_agent_service.py
│   ├── test_app.py
│   ├── test_app_agent.py
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

This keeps responsibilities localized and makes future expansion significantly easier.

---

# Subsystem Overview

Project ATLAS is composed of independent subsystems coordinated by `AtlasApp`.

Each subsystem owns a specific responsibility and communicates through well-defined interfaces.

Current subsystems include:

- Configuration
- Core
- Agent
- Models
- Memory
- Conversations
- Observability
- Permissions
- Filesystem
- Tools

Future releases will introduce:

- Planning
- Web Research
- Semantic Memory
- Desktop Automation
- Voice
- Vision
- Robotics

---

# Configuration Subsystem

Directory:

```text
atlas/config/
```

Responsibilities:

- Environment-variable loading
- Settings validation
- Default values
- Filesystem configuration
- Logging configuration
- Provider configuration

Primary classes:

- `Settings`
- `load_settings()`

No business logic exists inside the configuration subsystem.

It exists solely to provide validated configuration objects for the rest of the application.

---

# Core Subsystem

Directory:

```text
atlas/core/
```

The Core subsystem contains the primary application coordinator.

Main class:

```text
AtlasApp
```

AtlasApp owns the lifecycle of every request.

Responsibilities include:

- Processing CLI input
- Detecting built-in commands
- Building conversation context
- Calling the Agent
- Coordinating memory
- Coordinating conversations
- Coordinating permissions
- Coordinating tools
- Returning final responses
- Logging request execution

AtlasApp intentionally contains orchestration logic rather than business logic.

Subsystem-specific behavior remains inside the owning subsystem.

---

# Agent Subsystem

Directory:

```text
atlas/agent/
```

Version 1.0.0 introduces the first true ATLAS agent.

The Agent subsystem transforms natural-language requests into structured execution decisions.

Responsibilities include:

- Building structured prompts
- Presenting registered tools to the model
- Receiving structured model decisions
- Parsing JSON decisions
- Validating decision structure
- Validating requested tools
- Coordinating tool execution
- Coordinating permission checks
- Returning trusted tool results
- Managing pending confirmation requests

The agent never executes tools directly.

Instead it delegates execution through the existing Tool Framework.

---

## Agent Pipeline

```text
User Request
      │
      ▼
Prompt Builder
      │
      ▼
Model Provider
      │
      ▼
Structured JSON
      │
      ▼
Decision Parser
      │
      ▼
Decision Models
      │
      ▼
Tool Validation
      │
      ▼
Permission System
      │
      ▼
Tool Executor
      │
      ▼
Trusted Result
```

Each stage performs exactly one responsibility.

This layered design keeps the agent predictable and highly testable.

---

## Agent Components

### Prompt Builder

Responsible for constructing structured prompts.

Responsibilities:

- Build system instructions
- Inject conversation context
- Inject registered tools
- Inject parameter schemas
- Inject permission metadata
- Request structured JSON output

The prompt builder never interprets model responses.

---

### Decision Parser

Responsible for interpreting model output.

Responsibilities:

- Parse JSON
- Validate required fields
- Reject malformed responses
- Reject unknown structures
- Produce typed decision models

Invalid outputs never reach execution.

---

### Agent Service

The Agent Service coordinates the complete decision pipeline.

Responsibilities:

- Send prompts to the model
- Parse structured responses
- Validate tool requests
- Coordinate permissions
- Execute approved tools
- Return trusted tool output
- Manage confirmation state

It acts as the orchestration layer for the Agent subsystem.

---

### Decision Models

The agent uses strongly typed models rather than dictionaries.

Current models include:

- Direct response
- Tool request
- Pending tool request
- Tool execution result

Typed models reduce runtime ambiguity while improving maintainability.

---

# Model Subsystem

Directory:

```text
atlas/models/
```

Responsibilities:

- AI provider abstraction
- Local inference
- Cloud inference
- Structured-output support
- Provider configuration

Current providers:

- Mock
- OpenAI
- Ollama

The provider interface allows AtlasApp and the Agent subsystem to remain provider-independent.

---

## Provider Factory

Rather than constructing providers directly, ATLAS uses a provider factory.

Benefits include:

- Loose coupling
- Simplified testing
- Easy provider replacement
- Centralized configuration

Future providers can be added without modifying AtlasApp.

---

# Memory Subsystem

Directory:

```text
atlas/memory/
```

Responsibilities:

- Persistent storage
- Memory retrieval
- Remember command
- Forget command
- Context generation

Memory remains independent from conversations.

Explicit memories represent long-term information while conversations represent dialogue history.

---

# Conversation Subsystem

Directory:

```text
atlas/conversations/
```

Responsibilities:

- Conversation creation
- Message history
- Conversation switching
- Active conversation tracking
- Context reconstruction

Conversation history is provided to the Agent as context but remains owned by the Conversation subsystem.

The Agent never communicates directly with the database.

All persistence passes through the Conversation Service.

---

# Observability Subsystem

Directory:

```text
atlas/observability/
```

The observability subsystem provides structured logging throughout ATLAS.

Responsibilities:

- Request logging
- Startup logging
- Shutdown logging
- Performance timing
- Error logging
- Permission audit logging
- Tool audit logging
- Filesystem audit logging

Every significant operation is recorded through structured log entries.

Sensitive information such as conversation history, memory contents, API keys, and document contents are intentionally excluded from logs.

---

# Permission Subsystem

Directory:

```text
atlas/permissions/
```

The permission subsystem determines whether a requested tool is allowed to execute.

Responsibilities:

- Risk evaluation
- Permission decisions
- Confirmation handling
- Pending requests
- Audit logging

Current decision types:

```text
ALLOW
CONFIRM
DENY
```

Permission decisions are based entirely on registered tool metadata.

Current risk levels:

```text
LOW
MEDIUM
HIGH
```

Decision flow:

```text
Tool Request
      │
      ▼
Permission Policy
      │
      ▼
LOW ─────► Execute

MEDIUM ──► Wait for Confirmation

HIGH ────► Deny
```

The permission subsystem does not execute tools.

It only determines whether execution is permitted.

---

# Filesystem Subsystem

Directory:

```text
atlas/filesystem/
```

The filesystem subsystem provides secure access to local files.

Responsibilities:

- Path resolution
- Allowed-directory enforcement
- Directory listing
- File metadata
- Reading text files
- Writing text files
- Creating directories

The filesystem subsystem never performs permission evaluation.

Permission decisions are made before filesystem operations begin.

---

## Scoped Path Resolver

Every filesystem operation passes through the scoped path resolver.

Responsibilities:

- Normalize paths
- Resolve relative paths
- Reject path traversal
- Verify allowed directories

This guarantees that tools cannot escape configured workspace boundaries.

---

## FileSystemService

The FileSystemService performs the actual filesystem operations.

Examples include:

- List directory
- Read text
- Write text
- Create directory
- File information

The service intentionally contains no AI logic.

---

# Tool Framework

Directory:

```text
atlas/tools/
```

The tool framework provides a common execution model for every capability exposed to the Agent.

Responsibilities:

- Tool registration
- Tool discovery
- Argument validation
- Execution
- Result formatting
- Logging

Every tool shares the same interface.

Current built-in tools:

- Calculator
- Current Time
- List Directory
- File Information
- Read Text File
- Write Text File
- Create Directory
- Confirmation Demo

Future releases may add:

- Web Search
- Python Execution
- Desktop Automation
- Vision
- Robotics

without changing the architecture.

---

## Tool Registry

The Tool Registry owns every available tool.

Responsibilities:

- Register tools
- Lookup tools
- Enumerate definitions

The Agent never hardcodes available tools.

Instead it queries the registry dynamically.

This keeps prompt generation synchronized with the application's actual capabilities.

---

## Tool Executor

The Tool Executor is responsible for running validated tools.

Responsibilities:

- Validate arguments
- Execute tools
- Measure execution time
- Produce ToolResult objects
- Emit audit logs

The executor does not perform permission evaluation.

Permission decisions always occur earlier in the pipeline.

---

# Request Processing Pipeline

Version 1.0.0 introduces a layered request pipeline.

Every natural-language request follows the same architecture.

```text
User
 │
 ▼
Command Line Interface
 │
 ▼
AtlasApp
 │
 ▼
Built-in Command Detection
 │
 ├──────────────► Explicit Command
 │                    │
 │                    ▼
 │               Execute Immediately
 │
 ▼
Deterministic Routing
 │
 ├──────────────► Known Safe Pattern
 │                    │
 │                    ▼
 │             Create Tool Request
 │
 ▼
Agent Service
 │
 ▼
Prompt Builder
 │
 ▼
Model Provider
 │
 ▼
Structured JSON Decision
 │
 ▼
Decision Parser
 │
 ▼
Decision Models
 │
 ▼
Tool Validation
 │
 ▼
Permission Evaluation
 │
 ▼
Tool Execution
 │
 ▼
Trusted Tool Result
 │
 ▼
Conversation Storage
 │
 ▼
User
```

Every stage performs one responsibility.

This separation greatly improves:

- Maintainability
- Testing
- Reliability
- Security

---

# Deterministic Routing

Some requests are recognized before reaching the language model.

Examples include:

- Create a folder...
- Create a file...
- Write a file...

These requests are converted directly into structured tool requests.

Benefits include:

- Faster execution
- Lower model usage
- Predictable behavior
- Guaranteed permission evaluation

Deterministic routing reduces model hallucinations while preserving the agent architecture.

---

# Confirmation Workflow

Medium-risk operations pause before execution.

Current workflow:

```text
User Request
      │
      ▼
Agent
      │
      ▼
Permission Evaluation
      │
      ▼
CONFIRM
      │
      ▼
Pending Request Stored
      │
      ▼
User:
confirm yes
      │
      ▼
Execute Tool

or

confirm no
      │
      ▼
Discard Request
```

Pending requests exist only during the current application session.

No filesystem changes occur before approval.

---

# Data Storage

Current persistent storage includes:

```text
SQLite

├── Memory Database

└── Conversation Database
```

Local files:

```text
workspace/
logs/
data/
```

No cloud database currently exists.

All persistent storage remains local by default.

---

# Dependency Direction

Subsystem dependencies intentionally flow in one direction.

```text
CLI
 │
 ▼
AtlasApp
 │
 ├────────► Agent
 │
 ├────────► Memory
 │
 ├────────► Conversations
 │
 ├────────► Permissions
 │
 ├────────► Tools
 │
 ├────────► Filesystem
 │
 └────────► Models
```

Subsystems should avoid depending on each other whenever possible.

AtlasApp remains the central coordinator.

This architecture minimizes coupling and simplifies future expansion.

# Testing Architecture

Project ATLAS emphasizes automated testing as a first-class architectural requirement.

Every subsystem owns its own tests.

Current test coverage includes:

```text
tests/

├── test_agent_models.py
├── test_agent_parser.py
├── test_agent_prompt.py
├── test_agent_service.py
├── test_app.py
├── test_app_agent.py
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

Current automated coverage includes:

- Agent decision parsing
- Prompt generation
- Structured JSON validation
- Tool validation
- Tool registration
- Tool execution
- Permission evaluation
- Confirmation workflow
- Filesystem protection
- Conversation persistence
- Memory persistence
- Logging configuration
- Provider abstraction
- CLI behavior
- AtlasApp orchestration

Version 1.0.0 contains over **200 automated tests** covering every major subsystem.

Continuous Integration automatically runs:

- Ruff
- MyPy
- Pytest

on every pull request.

---

# Error Handling

ATLAS uses explicit exception types throughout the application.

Every subsystem owns its own exceptions.

Examples include:

```text
AgentError

PermissionError

ToolError

FileSystemError

MemoryDatabaseError

ConversationDatabaseError

ModelError
```

Exceptions are never silently ignored.

Instead they are:

- Logged
- Propagated
- Displayed with user-friendly messages

Unexpected failures should never leave ATLAS in an inconsistent state.

---

# Logging Architecture

Structured logging is available throughout every subsystem.

Major logging events include:

- Application startup
- Application shutdown
- Request processing
- Model requests
- Agent decisions
- Permission evaluation
- Confirmation decisions
- Tool execution
- Filesystem operations
- Memory operations
- Conversation operations
- Exceptions

Sensitive information is intentionally excluded from logs.

Examples include:

- Conversation history
- Memory contents
- API keys
- Environment variables
- File contents
- User documents

Logs exist for diagnostics rather than analytics.

---

# Security Architecture

Security is enforced through multiple independent layers.

Current layers include:

```text
User Request
      │
      ▼
Structured Agent Decision
      │
      ▼
Decision Validation
      │
      ▼
Registered Tool Verification
      │
      ▼
Argument Validation
      │
      ▼
Permission Evaluation
      │
      ▼
Confirmation Workflow
      │
      ▼
Scoped Filesystem
      │
      ▼
Tool Execution
```

Each layer assumes previous layers may fail.

This defense-in-depth architecture minimizes the impact of unexpected model behavior.

Current protections include:

- Registered tools only
- Structured JSON decisions
- Argument-schema validation
- Unknown-field rejection
- Unknown-tool rejection
- Permission enforcement
- Confirmation requirements
- Filesystem sandboxing
- Path traversal prevention
- Read/write limits
- Audit logging

No individual subsystem can bypass every protection.

---

# Current Limitations

Version 1.0.0 intentionally limits the Agent's autonomy.

Current limitations include:

- One tool per model-selected request
- No autonomous planning
- No recursive reasoning
- No background execution
- No task scheduling
- No web access
- No Python execution
- No desktop automation
- No unrestricted filesystem access
- No unrestricted shell execution

These limitations are intentional.

Future releases will expand capabilities gradually while maintaining strong security guarantees.

---

# Future Architecture

Future releases will expand the architecture without replacing the existing foundation.

Planned additions include:

```text
Planning Engine

↓

Multi-Step Agent Loop

↓

Semantic Memory

↓

Web Research

↓

Code Execution

↓

Desktop Automation

↓

Voice

↓

Vision

↓

Robotics
```

Every future subsystem will integrate through existing interfaces whenever practical.

This minimizes architectural disruption while enabling long-term growth.

---

# Scalability

ATLAS is designed to scale horizontally by adding capabilities rather than rewriting core systems.

Future expansion should primarily involve:

- Registering additional tools
- Adding new providers
- Creating new services
- Introducing new subsystems
- Extending prompt generation
- Expanding planning capabilities

AtlasApp should remain a lightweight coordinator rather than accumulating subsystem logic.

---

# Engineering Principles

Every subsystem should satisfy the following principles:

- Single responsibility
- Strong typing
- Comprehensive testing
- Explicit validation
- Structured logging
- Modular design
- Stable interfaces
- Clear documentation

Architectural consistency is preferred over rapid feature development.

---

# Long-Term Vision

The long-term goal of Project ATLAS is to become a complete AI operating system capable of safely coordinating complex workflows across multiple domains.

Future capabilities include:

- Autonomous engineering assistance
- Personal knowledge management
- Research assistance
- Desktop automation
- Voice interaction
- Vision understanding
- Robotics integration

These capabilities will be built incrementally on top of the existing architecture rather than replacing it.

---

# Architecture Summary

Version 1.0.0 establishes the first true agent architecture for Project ATLAS.

Major architectural capabilities now include:

- Modular subsystem design
- Provider-independent AI models
- Persistent memory
- Persistent conversations
- Structured logging
- Extensible tool framework
- Permission enforcement
- Secure filesystem access
- Structured agent decisions
- Dynamic tool selection
- Deterministic safety routing
- Trusted tool execution
- Confirmation-controlled actions
- Comprehensive automated testing

Future releases will build upon this foundation by introducing bounded multi-step planning, richer memory retrieval, additional tools, and broader interaction capabilities while preserving the modular architecture established in Version 1.0.0.

---

**Architecture Version:** v1.0.0

**Document Status:** Current

**Last Updated:** August 2026