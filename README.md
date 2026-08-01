<div align="center">

# PROJECT ATLAS

### A Modular, Local-First AI Operating System

*Inspired by JARVIS. Engineered for the real world.*

---

![Version](https://img.shields.io/badge/version-v0.9.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-informational)
![ATLAS CI](https://github.com/victoriajarocki/Project-ATLAS/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active%20Development-orange)

</div>

---

# Overview

Project ATLAS is a long-term software engineering project focused on building a modular, extensible, privacy-first AI operating system.

Rather than developing a traditional chatbot, ATLAS is being engineered as a complete AI platform capable of natural conversation, long-term memory, secure tool execution, local reasoning, engineering assistance, computer interaction, and eventually autonomous task execution.

Every subsystem is designed around clean interfaces, testability, documentation, and long-term maintainability so that new capabilities can be added without requiring architectural redesign.

Project ATLAS is intended to evolve over many years into a complete AI operating system.

---

# Vision

The long-term objective of ATLAS is to create an AI system capable of functioning as a:

- Personal engineering assistant
- Programming assistant
- Research assistant
- Knowledge management platform
- Automation system
- Computer interface
- Voice assistant
- Vision-enabled assistant
- Robotics control platform

The project emphasizes modular software engineering rather than rapid feature development.

Each subsystem is designed to remain independently maintainable while integrating seamlessly with the larger architecture.

---

# Core Design Principles

## Modular Architecture

Every major capability exists as an independent subsystem.

Examples include:

- AI Providers
- Memory
- Conversations
- Observability
- Tools
- Permissions
- Filesystem
- Planning
- Voice
- Vision

Each subsystem can evolve independently while maintaining stable public interfaces.

---

## Local-First

Whenever practical, computation happens locally.

Current local capabilities include:

- Local Ollama models
- Local SQLite databases
- Local conversation storage
- Local memory storage
- Local log files
- Local filesystem tools

Cloud services remain optional rather than mandatory.

---

## Privacy First

User information belongs to the user.

Current privacy features include:

- SQLite storage
- Local logging
- Environment-based secrets
- Scoped filesystem access
- Path traversal protection
- Risk-based permission controls
- Confirmation-controlled tool execution

Future versions will continue expanding local-first capabilities.

---

## Engineering First

Project ATLAS is engineered using modern software engineering practices including:

- Modular package architecture
- Strong typing
- Static analysis
- Unit testing
- Continuous integration
- Versioned releases
- Architecture documentation
- Changelog management
- Automated formatting
- Automated linting

The objective is to build production-quality software rather than experimental prototypes.

---

# Current Features

## AI Providers

- Mock provider
- OpenAI provider
- Ollama provider
- Provider factory architecture
- Environment-based configuration

---

## Persistent Memory

- SQLite-backed memory
- Remember command
- Forget command
- Memory IDs
- Automatic context injection
- Source-tracked storage

---

## Conversation Engine

- Multiple persistent conversations
- Conversation history
- Automatic restoration
- Conversation switching
- Conversation renaming
- Context reconstruction

---

## Observability

- Structured logging
- Request IDs
- Performance timing
- Startup diagnostics
- Audit logging
- Rotating log files

---

## Tool Framework

- Modular tool registry
- Shared execution pipeline
- JSON argument validation
- Risk classification
- Built-in tools
- Extensible plugin architecture

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

ATLAS includes a dedicated permission subsystem that evaluates every tool request before execution.

Current permission capabilities include:

- Low-risk automatic execution
- Medium-risk confirmation workflow
- High-risk denial
- Pending request management
- Audit logging
- Confirmation approval
- Confirmation denial

---

## Secure Filesystem

Version 0.9 introduces the first secure filesystem subsystem.

Current capabilities include:

- Workspace sandboxing
- Configurable allowed directories
- Secure path resolution
- UTF-8 text reading
- UTF-8 text writing
- Directory creation
- Directory listing
- File metadata inspection
- Maximum read limits
- Maximum write limits
- Path traversal protection

All filesystem operations remain confined to explicitly configured workspace directories.

---

# Current Project Status

| Component | Status |
|-----------|--------|
| Foundation | ✅ Complete |
| AI Providers | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversation Engine | ✅ Complete |
| Observability | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permission System | ✅ Complete |
| Secure Filesystem | ✅ Complete |
| Agent Framework | 🚧 Next Milestone |
| Web Research | ⏳ Planned |
| Semantic Memory | ⏳ Planned |
| Voice | ⏳ Planned |
| Vision | ⏳ Planned |
| Robotics | ⏳ Long-Term |

---

# Current Repository Statistics

Current release:

- **Version:** v0.9.0
- **Python:** 3.13+
- **Architecture:** Modular
- **Unit Tests:** 131 Passing
- **Static Type Checking:** MyPy
- **Formatting:** Ruff
- **Linting:** Ruff
- **CI:** GitHub Actions
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

Clone the repository.

```bash
git clone https://github.com/victoriajarocki/Project-ATLAS.git
```

Enter the project directory.

```bash
cd Project-ATLAS
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Install ATLAS in editable development mode.

```bash
pip install -e ".[dev]"
```

---

# Configuration

ATLAS is configured entirely through environment variables.

Create a local configuration file.

```text
.env
```

Example configuration:

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model

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

Filesystem access is intentionally restricted to configured workspace directories.

---

# Running ATLAS

Launch the application.

```bash
atlas
```

Example startup:

```text
==================================================
ATLAS v0.9.0
Personal AI Operating System

Model provider: Mock

Persistent memory: Enabled
Conversation sessions: Enabled
Tool system: Enabled
Permission system: Enabled

==================================================
```

---

# Example Commands

## Persistent Memory

Remember information.

```text
remember My L2 rocket is named Wraith.
```

View stored memories.

```text
memories
```

Delete a memory.

```text
forget 3
```

---

## Conversation Management

Create a new conversation.

```text
new chat Rocket Design
```

View conversations.

```text
chats
```

Switch conversations.

```text
use chat 2
```

Rename the active conversation.

```text
rename chat Research Notes
```

Display recent history.

```text
history
```

---

## Built-in Tools

List available tools.

```text
tools
```

Calculator

```text
tool calculator {"expression":"15*(6+3)"}
```

Current time

```text
tool current_time {}
```

---

## Filesystem Tools

List files.

```text
tool list_directory {"path":"."}
```

Read a text file.

```text
tool read_text_file {"path":"Rocket Design/notes.txt"}
```

Inspect file metadata.

```text
tool file_info {"path":"Rocket Design/notes.txt"}
```

Create a directory.

```text
tool create_directory {"path":"Rocket Design"}
```

Write a file.

```text
tool write_text_file {
    "path":"Rocket Design/notes.txt",
    "content":"Project ATLAS"
}
```

---

## Confirmation Workflow

Medium-risk tools require explicit user approval.

Approve execution.

```text
confirm yes
```

Reject execution.

```text
confirm no
```

ATLAS never executes confirmation-controlled tools until approval is received.

---

# Development Workflow

Run formatting.

```bash
ruff format .
```

Run linting.

```bash
ruff check .
```

Run static type checking.

```bash
mypy src
```

Run all tests.

```bash
pytest
```

Current automated test suite:

- 131 passing tests
- Filesystem subsystem tests
- Permission workflow tests
- Conversation tests
- Memory tests
- Tool framework tests
- Logging tests
- Model provider tests

---

# Continuous Integration

Every pull request automatically performs:

- Ruff formatting verification
- Ruff linting
- MyPy type checking
- Complete unit test suite

This ensures every merge into the main branch maintains project quality standards.

---

# Documentation

Additional documentation is available throughout the repository.

| Document | Description |
|----------|-------------|
| `ARCHITECTURE.md` | Complete system architecture |
| `CHANGELOG.md` | Version history |
| `ROADMAP.md` | Development roadmap |
| `docs/installation.md` | Installation guide |
| `docs/configuration.md` | Environment configuration |
| `docs/development.md` | Development workflow |
| `docs/tools.md` | Tool framework |
| `docs/permissions.md` | Permission subsystem |
| `docs/filesystem.md` | Secure filesystem subsystem |

---

# Current Release

## Project ATLAS v0.9.0

ATLAS v0.9.0 introduces the first secure filesystem subsystem.

Major additions include:

- Scoped filesystem architecture
- Secure path resolver
- FileSystemService
- Read text files
- Write text files
- Create directories
- Directory listing
- File metadata inspection
- JSON schema validation
- Shared argument validation
- Workspace sandboxing
- Path traversal protection
- Permission-controlled filesystem writes
- Expanded automated test coverage

---

# Long-Term Roadmap

Project ATLAS is being developed as a long-term engineering project through incremental, versioned milestones.

## Completed

- ✅ v0.1.0 — Foundation
- ✅ v0.2.0 — Model Provider Architecture
- ✅ v0.3.0 — Local AI (Ollama)
- ✅ v0.4.0 — Persistent Memory
- ✅ v0.5.0 — Conversation Sessions
- ✅ v0.6.0 — Structured Logging
- ✅ v0.7.0 — Tool Framework
- ✅ v0.8.0 — Permission System
- ✅ v0.9.0 — Secure Filesystem

---

## Next Milestone

### v1.0.0 — Agent Framework

The next major milestone transitions ATLAS from executing individual commands to reasoning about complex tasks.

Planned capabilities include:

- Multi-step task planning
- Automatic tool selection
- Sequential tool execution
- Internal reasoning pipeline
- Action planning
- Agent execution loop
- Task completion summaries

Example:

```text
You:
Create a folder called Rockets,
create notes.txt,
and write "Project Wraith"
inside it.
```

ATLAS will internally plan:

```text
Thought
↓

Create directory

↓

Create file

↓

Write contents

↓

Return completion summary
```

This represents the transition from a command-driven assistant to an intelligent AI agent.

---

## Future Development

Planned future milestones include:

### AI

- Semantic memory
- Long-term memory ranking
- Memory retrieval optimization
- Multiple reasoning modes

### Tools

- Web search
- Weather
- Email
- Calendar
- PDF reader
- Code execution
- Git integration

### Computer Interaction

- Desktop automation
- Keyboard control
- Mouse control
- Application launching
- Screen understanding

### Voice

- Speech recognition
- Streaming conversation
- Wake word
- Natural voice synthesis

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

---

# Contributing

Project ATLAS is currently developed as a long-term personal engineering project.

Although outside contributions are not currently being accepted, the repository follows modern software engineering practices including:

- Feature branches
- Pull requests
- Versioned releases
- Automated testing
- Continuous integration
- Static analysis
- Comprehensive documentation

Future community contributions may be supported as the architecture matures.

---

# Version History

| Version | Major Feature |
|----------|---------------|
| v0.1.0 | Project Foundation |
| v0.2.0 | Model Provider Architecture |
| v0.3.0 | Ollama Integration |
| v0.4.0 | Persistent Memory |
| v0.5.0 | Conversation Sessions |
| v0.6.0 | Structured Logging |
| v0.7.0 | Tool Framework |
| v0.8.0 | Permission System |
| v0.9.0 | Secure Filesystem |

A complete history of every release is available in:

- `CHANGELOG.md`
- GitHub Releases

---

# Engineering Philosophy

Project ATLAS is built around one guiding principle:

> Build the architecture first. Build capabilities second.

Every subsystem is designed with long-term maintainability, modularity, and extensibility as primary goals.

Rather than optimizing for rapid feature development, ATLAS prioritizes:

- Clean architecture
- Stable interfaces
- Thorough testing
- Comprehensive documentation
- Versioned development
- Incremental improvement

The objective is not simply to create another AI assistant, but to engineer a software platform capable of supporting years of future development.

---

# Project Status

Current release:

**Project ATLAS v0.9.0**

Current implementation includes:

- ✅ Modular architecture
- ✅ Multiple AI providers
- ✅ Persistent memory
- ✅ Conversation management
- ✅ Structured logging
- ✅ Tool framework
- ✅ Permission system
- ✅ Secure filesystem
- ✅ Continuous integration
- ✅ Comprehensive documentation
- ✅ 131 automated tests

Development is actively continuing toward the v1.0.0 Agent Framework milestone.

---

# License

Project ATLAS is released under the MIT License.

See the `LICENSE` file for complete licensing information.

---

<div align="center">

## Project ATLAS

*A modular AI operating system engineered for long-term growth.*

**Current Version:** **v0.9.0**

**Next Milestone:** **v1.0.0 — Agent Framework**

---

*"Build the architecture today for the intelligence of tomorrow."*

</div>