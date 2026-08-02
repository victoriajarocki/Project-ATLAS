<div align="center">

# PROJECT ATLAS

### A Modular, Local-First AI Operating System

*Inspired by JARVIS. Engineered for the real world.*

---

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-informational)
![ATLAS CI](https://github.com/victoriajarocki/Project-ATLAS/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active%20Development-orange)

</div>

---

# Overview

Project ATLAS is a long-term software engineering project focused on building a modular, extensible, privacy-first AI operating system.

Rather than functioning as a traditional chatbot, ATLAS is engineered as a complete AI platform capable of natural conversation, persistent memory, secure tool execution, local reasoning, engineering assistance, computer interaction, and eventually autonomous task execution.

Version 1.0.0 introduces the first agent foundation. ATLAS can now interpret ordinary natural-language requests, decide whether a registered tool is needed, validate structured tool requests, apply permission policies, execute approved tools, and return trusted results.

Every subsystem is designed around stable interfaces, strong typing, automated testing, documentation, and long-term maintainability.

---

# Vision

The long-term objective of Project ATLAS is to create an AI system capable of functioning as a:

- Personal engineering assistant
- Programming assistant
- Research assistant
- Knowledge-management platform
- Automation system
- Computer interface
- Voice assistant
- Vision-enabled assistant
- Robotics-control platform

The project emphasizes modular software engineering rather than rapid feature development.

Each subsystem is designed to remain independently maintainable while integrating with the larger ATLAS architecture.

---

# Core Design Principles

## Modular Architecture

Every major capability exists as an independent subsystem.

Current subsystems include:

- Agent
- AI Providers
- Configuration
- Conversations
- Filesystem
- Memory
- Observability
- Permissions
- Tools

Planned subsystems include:

- Planning
- Web Research
- Voice
- Vision
- Desktop Control
- Robotics

Each subsystem can evolve independently while maintaining stable public interfaces.

---

## Local-First

Whenever practical, computation happens locally.

Current local capabilities include:

- Local AI inference through Ollama
- Local SQLite databases
- Local conversation storage
- Local memory storage
- Local rotating log files
- Local filesystem tools
- Local agent decisions
- Local permission enforcement

Cloud model providers remain optional rather than mandatory.

---

## Privacy First

User information belongs to the user.

Current privacy and security features include:

- Local SQLite storage
- Local application logging
- Environment-based secrets
- Scoped filesystem access
- Configurable allowed directories
- Path-traversal protection
- Risk-based permission controls
- Confirmation-controlled state changes
- High-risk tool denial
- Tool-argument validation
- Logs that exclude complete message and file contents

Future releases will continue expanding local-first operation and user-controlled authorization.

---

## Engineering First

Project ATLAS uses modern software-engineering practices including:

- Modular package architecture
- Abstract interfaces
- Strong typing
- Static analysis
- Unit and integration testing
- Continuous integration
- Versioned releases
- Architecture documentation
- Changelog management
- Automated formatting
- Automated linting
- Security-oriented validation

The objective is to build production-quality software rather than an experimental prototype.

---

# Current Features

## Agent Foundation

Version 1.0.0 introduces the first ATLAS agent subsystem.

Current agent capabilities include:

- Natural-language request interpretation
- Structured agent decisions
- Automatic tool selection
- Dynamic tool-catalog generation
- JSON-schema-constrained Ollama decisions
- Strict structured-response parsing
- Tool-name validation
- Tool-argument validation
- Permission-policy integration
- Confirmation-controlled state changes
- Direct trusted tool-result responses
- Deterministic routing for recognized file and directory creation requests
- Conversation-context integration
- Persistent storage of agent responses
- Backward-compatible explicit tool commands

ATLAS can now interpret requests such as:

```text
What is 347 multiplied by 982?
```

and automatically select the calculator.

It can also interpret:

```text
What files are in my workspace?
```

and automatically select the directory-listing tool.

State-changing requests remain protected:

```text
Create a file called hello.txt that says Hello World.
```

ATLAS routes the request to `write_text_file`, evaluates its risk, and requires explicit confirmation before execution.

---

## AI Providers

- Mock provider
- OpenAI provider
- Ollama provider
- Provider-factory architecture
- Environment-based provider selection
- Normal response generation
- Structured response generation
- Ollama JSON-schema output
- Ollama thinking suppression
- Local-model keep-alive support
- Defensive reasoning-output cleanup

---

## Persistent Memory

- SQLite-backed memory
- Explicit `remember` command
- Explicit `forget` command
- Memory IDs
- Memory categories
- Source tracking
- Automatic context injection
- Local persistence

---

## Conversation Engine

- Multiple persistent conversations
- Persistent user and assistant messages
- Conversation history
- Automatic restoration
- Conversation switching
- Conversation renaming
- Context reconstruction
- Agent-context integration

---

## Observability

- Structured logging
- Request IDs
- Request timing
- Tool-execution timing
- Startup diagnostics
- Permission audit logging
- Confirmation audit logging
- Rotating log files
- Controlled error logging

---

## Tool Framework

- Modular tool interface
- Tool definitions
- JSON parameter schemas
- Central tool registry
- Shared execution pipeline
- Shared argument validation
- Tool-risk classification
- Confirmation metadata
- Structured tool results
- Execution timing
- Defense-in-depth validation
- Explicit command execution
- Model-selected execution

Current built-in tools include:

- Calculator
- Current Time
- Confirmation Demo
- Directory Listing
- File Information
- Read Text File
- Create Directory
- Write Text File

---

## Permission System

ATLAS includes a dedicated permission subsystem that evaluates tool requests before execution.

Current permission capabilities include:

- Low-risk automatic execution
- Medium-risk confirmation
- High-risk denial
- Pending-request management
- Approval handling
- Denial handling
- Permission audit logging
- Confirmation audit logging
- Shared behavior for explicit and agent-selected tools

ATLAS does not execute confirmation-controlled tools until the user enters:

```text
confirm yes
```

The user may deny the request with:

```text
confirm no
```

---

## Secure Filesystem

ATLAS includes a scoped filesystem subsystem designed to prevent unrestricted computer access.

Current capabilities include:

- Workspace sandboxing
- Configurable allowed directories
- Secure path resolution
- Relative-path support
- Directory listing
- File metadata inspection
- UTF-8 text reading
- UTF-8 text writing
- Directory creation
- Maximum read limits
- Maximum write limits
- Parent-traversal rejection
- Outside-scope path rejection
- Existing-file protection
- Confirmation-controlled writes
- Confirmation-controlled directory creation

All filesystem operations remain confined to explicitly configured directories.

ATLAS does not currently support:

- File deletion
- Arbitrary shell access
- Unrestricted filesystem access
- Binary-file modification
- Recursive mass operations

---

# Current Project Status

| Component | Status |
|---|---|
| Foundation | ✅ Complete |
| AI Providers | ✅ Complete |
| Local AI | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversation Engine | ✅ Complete |
| Observability | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permission System | ✅ Complete |
| Secure Filesystem | ✅ Complete |
| Agent Foundation | ✅ Complete |
| Multi-Step Agent Loop | ⏳ Planned |
| Semantic Memory | ⏳ Planned |
| Web Research | ⏳ Planned |
| Voice | ⏳ Planned |
| Vision | ⏳ Planned |
| Desktop Control | ⏳ Planned |
| Robotics | ⏳ Long-Term |

---

# Current Repository Statistics

Current release:

- **Version:** v1.0.0
- **Python:** 3.13+
- **Architecture:** Modular and local-first
- **Automated Tests:** 204 passing
- **Static Type Checking:** MyPy
- **Formatting:** Ruff
- **Linting:** Ruff
- **Continuous Integration:** GitHub Actions
- **License:** MIT

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
├── logs/
│
├── src/
│   └── atlas/
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── exceptions.py
│       │   ├── models.py
│       │   ├── parser.py
│       │   ├── prompt.py
│       │   └── service.py
│       │
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
│   ├── test_app_agent.py
│   └── ...
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

---

# Installation

Clone the repository:

```bash
git clone https://github.com/victoriajarocki/Project-ATLAS.git
```

Enter the project directory:

```bash
cd Project-ATLAS
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Install ATLAS in editable development mode:

```bash
python -m pip install -e ".[dev]"
```

---

# Configuration

ATLAS is configured through environment variables.

Create a local configuration file:

```text
.env
```

Example configuration:

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b

OPENAI_API_KEY=

OLLAMA_HOST=http://localhost:11434

ATLAS_MEMORY_DATABASE=data/atlas_memory.db

ATLAS_LOG_DIRECTORY=logs
ATLAS_LOG_LEVEL=INFO
ATLAS_LOG_MAX_BYTES=5000000
ATLAS_LOG_BACKUP_COUNT=5

ATLAS_ALLOWED_DIRECTORIES=workspace
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

Filesystem access is restricted to configured directories.

The real `.env` file must remain excluded from Git.

---

# Running ATLAS

Launch the application:

```bash
atlas
```

Example startup:

```text
==================================================
ATLAS v1.0.0
Personal AI Operating System
Model provider: Ollama
Persistent memory: Enabled
Conversation sessions: Enabled
Tool system: Enabled
Permission system: Enabled
Agent system: Enabled
Active chat: 1
==================================================
```

---

# Natural-Language Agent Examples

## Direct Response

```text
You: What is the capital of Poland?

ATLAS: The capital of Poland is Warsaw.
```

## Automatic Calculator Selection

```text
You: What is 347 multiplied by 982?

ATLAS: 340754
```

## Automatic Workspace Listing

```text
You: What files are in my workspace?

ATLAS:
file: .gitkeep (size: 0 bytes)
file: agent-test.txt (size: 27 bytes)
```

## Automatic File Reading

```text
You: Read agent-test.txt.

ATLAS: Project ATLAS agent test.
```

## Confirmation-Controlled Directory Creation

```text
You: Create a folder called Rocket Design.

ATLAS: Tool create_directory requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.

You: confirm yes

ATLAS: Created directory: Rocket Design
```

## Confirmation-Controlled File Creation

```text
You: Create a file called hello.txt that says Hello World.

ATLAS: Tool write_text_file requires confirmation.
Risk level: medium.
Reason: This tool requires explicit user confirmation before execution.
Use 'confirm yes' to approve or 'confirm no' to deny.

You: confirm yes

ATLAS: Created file: hello.txt (11 characters)
```

## Current Local Time

```text
You: What time is it?

ATLAS:
Current local time

Saturday, August 01, 2026
8:10:48 PM EDT
```

---

# Explicit Commands

Natural-language agent behavior is now the primary interaction mode, but explicit commands remain available for control, testing, and debugging.

## Persistent Memory

Remember information:

```text
remember My L2 rocket is named Wraith.
```

View stored memories:

```text
memories
```

Delete a memory:

```text
forget 3
```

---

## Conversation Management

Create a new conversation:

```text
new chat Rocket Design
```

View conversations:

```text
chats
```

Switch conversations:

```text
use chat 2
```

Rename the active conversation:

```text
rename chat Research Notes
```

Display recent history:

```text
history
```

---

## Explicit Tool Commands

List registered tools:

```text
tools
```

Run the calculator:

```text
tool calculator {"expression":"15*(6+3)"}
```

Read the current local time:

```text
tool current_time {}
```

List workspace contents:

```text
tool list_directory {"path":"."}
```

Read a text file:

```text
tool read_text_file {"path":"Rocket Design/notes.txt"}
```

Inspect file metadata:

```text
tool file_info {"path":"Rocket Design/notes.txt"}
```

Create a directory:

```text
tool create_directory {"path":"Rocket Design"}
```

Write a text file:

```text
tool write_text_file {"path":"Rocket Design/notes.txt","content":"Project ATLAS"}
```

---

# Confirmation Workflow

Medium-risk tools require explicit approval.

Approve a pending request:

```text
confirm yes
```

Reject a pending request:

```text
confirm no
```

ATLAS blocks unrelated requests while a confirmation-controlled action is pending.

High-risk tools are denied by the default permission policy.

---

# Agent Execution Flow

A normal v1.0.0 agent request follows this pipeline:

```text
User Message
    ↓
AtlasApp
    ↓
Command Detection
    ↓
Deterministic Safety Routing
    ↓
Agent Prompt Builder
    ↓
Model Structured Decision
    ↓
Agent Decision Parser
    ↓
Tool and Argument Validation
    ↓
Permission Evaluation
    ↓
Tool Execution or Confirmation
    ↓
Trusted Tool Result
    ↓
Conversation Storage
    ↓
User Response
```

For tool-assisted requests, ATLAS returns the trusted tool result directly. This avoids a second model call, reduces latency, and prevents reasoning or prompt text from leaking into user-facing output.

---

# Agent Safety Model

Version 1.0.0 intentionally limits agent autonomy.

Current safeguards include:

- Exactly one model-selected tool per request
- Strict structured decision parsing
- Registered tools only
- Tool-schema validation
- Permission evaluation before execution
- Confirmation for state-changing tools
- High-risk tool denial
- Scoped filesystem access
- Deterministic routing for recognized file and directory creation
- No arbitrary shell execution
- No unrestricted file access
- No autonomous background execution
- No unbounded reasoning loop
- No self-modifying prompts

Multi-step autonomous planning is intentionally deferred to a later release.

---

# Development Workflow

Run formatting:

```bash
ruff format .
```

Verify formatting:

```bash
ruff format --check .
```

Run linting:

```bash
ruff check .
```

Run static type checking:

```bash
mypy src
```

Run all tests:

```bash
pytest
```

Check for whitespace errors:

```bash
git diff --check
```

The current automated suite contains **204 passing tests**, including:

- Agent decision-model tests
- Agent parser tests
- Agent prompt tests
- Agent service tests
- Application-level agent integration tests
- Filesystem tests
- Permission workflow tests
- Conversation tests
- Memory tests
- Tool framework tests
- Logging tests
- Model-provider tests
- Structured-output tests
- Deterministic action-routing tests

---

# Continuous Integration

Every push and pull request runs:

- Ruff lint checks
- Ruff formatting verification
- MyPy static type checking
- Complete pytest suite

This ensures changes meet the project's quality requirements before merging.

---

# Documentation

| Document | Description |
|---|---|
| `ARCHITECTURE.md` | Complete system architecture |
| `CHANGELOG.md` | Version and release history |
| `ROADMAP.md` | Planned development milestones |
| `docs/agent.md` | Agent subsystem and execution model |
| `docs/installation.md` | Installation guide |
| `docs/configuration.md` | Environment configuration |
| `docs/development.md` | Development and contribution workflow |
| `docs/tools.md` | Tool framework |
| `docs/permissions.md` | Permission subsystem |
| `docs/filesystem.md` | Secure filesystem subsystem |

---

# Current Release

## Project ATLAS v1.0.0 — Agent Foundation

Version 1.0.0 transitions ATLAS from a command-driven assistant into a constrained, tool-using AI agent.

Major additions include:

- Dedicated agent package
- Agent decision models
- Structured decision parser
- Dynamic tool catalog
- Agent prompt builder
- Agent orchestration service
- Natural-language tool selection
- JSON-schema-constrained Ollama decisions
- Tool-result safety improvements
- Permission-system integration
- Model-selected confirmation workflow
- Deterministic file-creation routing
- Deterministic directory-creation routing
- User-friendly local-time output
- Agent integration with conversation history
- 204 passing automated tests

Version 1.0.0 remains intentionally limited to one model-selected tool per request.

---

# Development Roadmap

## Completed Releases

- ✅ v0.1.0 — Foundation
- ✅ v0.2.0 — Model Provider Architecture
- ✅ v0.3.0 — Local AI with Ollama
- ✅ v0.4.0 — Persistent Memory
- ✅ v0.5.0 — Conversation Sessions
- ✅ v0.6.0 — Structured Logging
- ✅ v0.7.0 — Tool Framework
- ✅ v0.8.0 — Permission System
- ✅ v0.9.0 — Secure Filesystem
- ✅ v1.0.0 — Agent Foundation

---

## Planned Development

Future releases may include:

### Agent Capabilities

- Multi-step tool execution
- Agent-step limits
- Replanning after tool results
- Failed-tool recovery
- Task-completion summaries
- Explicit task cancellation
- Persistent plans

### Memory

- Semantic retrieval
- Embedding-based search
- Memory relevance ranking
- Memory consolidation
- Automatic memory suggestions
- Source-aware retrieval

### Tools

- Web research
- Weather
- Email
- Calendar
- PDF reading
- Code execution
- Git integration
- Application launching

### Computer Interaction

- Desktop automation
- Keyboard control
- Mouse control
- Window management
- Screen understanding

### Voice

- Speech recognition
- Streaming conversation
- Wake-word detection
- Local speech synthesis

### Vision

- Image understanding
- Screenshot analysis
- OCR
- Camera input

### Engineering

- CAD assistance
- MATLAB integration
- Python execution
- Engineering calculations
- Scientific workflows

### Robotics

- Sensor integration
- Robot control
- Autonomous planning
- Real-world interaction

See `ROADMAP.md` for the complete development plan.

---

# Contributing

Project ATLAS is currently developed as a long-term personal engineering project.

Although outside contributions are not currently being accepted, the repository follows professional software-development practices including:

- Feature branches
- Pull requests
- Linked issues
- Milestones
- Versioned releases
- Automated testing
- Continuous integration
- Static analysis
- Architecture documentation
- Release notes

Future community contributions may be supported as the architecture matures.

---

# Version History

| Version | Major Feature |
|---|---|
| v0.1.0 | Project Foundation |
| v0.2.0 | Model Provider Architecture |
| v0.3.0 | Ollama Integration |
| v0.4.0 | Persistent Memory |
| v0.5.0 | Conversation Sessions |
| v0.6.0 | Structured Logging |
| v0.7.0 | Tool Framework |
| v0.8.0 | Permission System |
| v0.9.0 | Secure Filesystem |
| v1.0.0 | Agent Foundation |

A complete history is available in:

- `CHANGELOG.md`
- GitHub Releases

---

# Engineering Philosophy

Project ATLAS is built around one guiding principle:

> Build the architecture first. Build capabilities second.

Every subsystem is designed with maintainability, modularity, security, and extensibility as primary goals.

Rather than optimizing only for rapid feature development, ATLAS prioritizes:

- Clean architecture
- Stable interfaces
- Explicit permissions
- Thorough testing
- Comprehensive documentation
- Versioned development
- Incremental improvement
- Safe failure behavior

The objective is not simply to create another chatbot, but to engineer a software platform capable of supporting years of future development.

---

# Project Status

Current release:

**Project ATLAS v1.0.0 — Agent Foundation**

Current implementation includes:

- ✅ Modular architecture
- ✅ Multiple AI providers
- ✅ Local Ollama inference
- ✅ Persistent memory
- ✅ Conversation management
- ✅ Structured logging
- ✅ Tool framework
- ✅ Permission system
- ✅ Secure filesystem
- ✅ Natural-language tool selection
- ✅ Structured agent decisions
- ✅ Confirmation-controlled agent actions
- ✅ Deterministic state-change routing
- ✅ Continuous integration
- ✅ Comprehensive documentation
- ✅ 204 automated tests

Development is actively continuing beyond the v1.0.0 agent foundation.

---

# License

Project ATLAS is released under the MIT License.

See the `LICENSE` file for complete licensing information.

---

<div align="center">

## Project ATLAS

*A modular AI operating system engineered for long-term growth.*

**Current Version:** **v1.0.0**

**Current Milestone:** **Agent Foundation Complete**

---

*"Build the architecture today for the intelligence of tomorrow."*

</div>