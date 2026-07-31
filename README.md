<div align="center">

# PROJECT ATLAS

### A Modular, Local-First AI Operating System

*Inspired by JARVIS. Engineered for the real world.*

---

![Version](https://img.shields.io/badge/version-v0.7.0-blue)
![Python](https://img.shields.io/badge/python-3.13+-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Windows-informational)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active%20Development-orange)

</div>

---

# Overview

Project ATLAS is a long-term engineering project focused on building a modular, extensible, and privacy-first AI operating system.

Rather than creating a single chatbot, the goal of ATLAS is to build a complete personal AI platform capable of natural conversation, long-term memory, secure tool execution, engineering assistance, computer interaction, and eventually robotics integration.

ATLAS is designed from the beginning around software engineering principles including modular architecture, extensibility, testing, documentation, and maintainability.

---

# Vision

The long-term vision of Project ATLAS is to create an AI system that can act as:

- Personal engineering assistant
- Research assistant
- Programming assistant
- Knowledge management system
- Automation platform
- Voice assistant
- Computer interface
- Robotics control platform

while remaining modular enough that entirely new capabilities can be added without redesigning the existing architecture.

---

# Core Design Principles

Project ATLAS is built around several guiding principles.

## Modular Architecture

Every major capability exists as an independent subsystem.

Examples include:

- Models
- Memory
- Conversations
- Logging
- Tools
- Voice
- Vision
- Planning

Each subsystem can evolve independently.

---

## Local-First

Whenever practical, computation happens locally.

ATLAS supports:

- Local LLMs through Ollama
- Local memory storage
- Local conversation history
- Local logging

Cloud services remain optional rather than mandatory.

---

## Privacy First

User data belongs to the user.

Current privacy features include:

- Local SQLite databases
- Local log files
- Configurable AI providers
- Environment-based secrets
- Ignored sensitive files
- Source-tracked memory

---

## Extensibility

ATLAS is designed to grow over many years.

New functionality is added through modular interfaces rather than modifying existing systems.

This minimizes breaking changes while encouraging long-term maintainability.

---

# Current Features

## AI Providers

- Mock provider
- OpenAI provider
- Ollama provider

---

## Persistent Memory

- SQLite-backed memory
- Remember command
- Forget command
- Memory IDs
- Context injection

---

## Conversation Engine

- Multiple persistent conversations
- Conversation history
- Conversation switching
- Conversation renaming
- Automatic context restoration

---

## Structured Logging

- Request IDs
- Performance timing
- Rotating log files
- Startup logging
- Error logging
- Audit records

---

## Tool Framework

- Modular tool registry
- Safe tool execution
- Tool risk classifications
- Calculator tool
- Current time tool

---

# Current Project Status

| Component | Status |
|-----------|--------|
| Foundation | ✅ Complete |
| Model Providers | ✅ Complete |
| Local AI | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversations | ✅ Complete |
| Logging | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permissions | 🚧 In Progress |
| Voice | ⏳ Planned |
| Vision | ⏳ Planned |
| Robotics | ⏳ Planned |

---

# Repository Structure

```text
Project-ATLAS/

src/
    atlas/
        config/
        conversations/
        core/
        memory/
        models/
        observability/
        tools/

tests/

README.md
CHANGELOG.md
ROADMAP.md
ARCHITECTURE.md
LICENSE
```

---

# Installation

Clone the repository.

```bash
git clone https://github.com/YOUR_USERNAME/Project-ATLAS.git
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

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the project.

```bash
pip install -e ".[dev]"
```

Launch ATLAS.

```bash
atlas
```

---

# Development

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

Run unit tests.

```bash
pytest
```

---

# Documentation

Additional project documentation is available in:

- `ROADMAP.md`
- `ARCHITECTURE.md`
- `CHANGELOG.md`

More documentation will be added as the project grows.

---

# Current Version

Current Release

**v0.7.0**

Recent additions include:

- Tool registry
- Tool execution framework
- Calculator tool
- Current time tool
- Risk-based tool definitions

---

# Long-Term Roadmap

The ATLAS roadmap currently includes development of:

- Permission system
- Secure computer control
- File system tools
- Web research tools
- Semantic memory
- Voice interface
- Vision
- Desktop application
- Engineering integrations
- Robotics platform

See `ROADMAP.md` for the complete development roadmap.

---

# Philosophy

ATLAS is not intended to be another chatbot.

The objective is to engineer a long-lived AI operating system whose capabilities can expand over time without requiring architectural redesign.

Every version is built with long-term maintainability, modularity, and extensibility as primary goals.

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.