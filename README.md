# Project ATLAS

<p align="center">

**A modular, local-first AI operating system and lifelong engineering partner.**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-v1.0.0-orange.svg)](CHANGELOG.md)
[![Tests](https://img.shields.io/badge/Tests-204%20Passing-success.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Modular-blueviolet.svg)]()

</p>

---

# Overview

Project ATLAS is a long-term software engineering project focused on building a modular, local-first AI platform capable of assisting with engineering, research, programming, automation, and long-running technical projects.

Unlike traditional chatbots, ATLAS is being developed as an extensible operating platform where every capability is introduced deliberately through modular subsystems with clearly defined security boundaries.

Current capabilities include:

- Local AI inference through Ollama
- Multiple interchangeable model providers
- Persistent long-term memory
- Persistent conversations
- Structured logging
- Extensible tool framework
- Permission-controlled execution
- Secure filesystem access
- Natural-language agent behavior

ATLAS is designed around one central philosophy:

> **Build the architecture first. Add intelligence second.**

---

# Project Direction

Version **v1.0.0** marks the completion of the first architectural phase of Project ATLAS.

The initial releases focused on building a stable foundation:

- Provider abstraction
- Local model support
- Persistent memory
- Conversation management
- Logging
- Tool execution
- Permission enforcement
- Secure filesystem
- Natural-language agent execution

With those systems now complete, development shifts toward making ATLAS progressively more capable rather than simply adding infrastructure.

The current development progression is:

```text
Performance
    ↓
Current Knowledge
    ↓
Reasoning
    ↓
Relevant Memory
    ↓
Project Intelligence
    ↓
Engineering Capability
    ↓
Natural Interfaces
    ↓
Physical-System Integration
```

This ordering is intentional.

A fast assistant is more useful than a slow assistant with many features.

An assistant with current knowledge is more useful than one that confidently answers outdated information.

An assistant that reasons carefully is more valuable than one that attempts unrestricted autonomy.

---

# Vision

Project ATLAS is being engineered to become a lifelong engineering partner rather than simply another AI chatbot.

The long-term goal is to create a modular AI operating system capable of assisting with engineering, programming, research, manufacturing, project management, and scientific work while remaining transparent, permission-controlled, and privacy-focused.

Future capability areas include:

- Engineering assistance
- Scientific computing
- Programming
- Manufacturing support
- Rocket engineering
- Research
- Desktop automation
- Voice interaction
- Vision understanding
- Spatial computing
- Robotics coordination

The long-term mission intentionally extends well beyond the current implementation.

Supporting documentation:

- `ROADMAP.md`
- `docs/vision.md`
- `docs/future_backlog.md`

---

# Current Capabilities

## AI Providers

- Mock provider
- OpenAI provider
- Ollama provider
- Provider abstraction
- Runtime provider selection

---

## Memory

- Persistent SQLite database
- Explicit memory creation
- Memory deletion
- Memory retrieval
- Memory categories
- Source tracking

---

## Conversations

- Multiple conversations
- Conversation history
- Conversation switching
- Conversation renaming
- Automatic conversation restoration

---

## Tool Framework

Built-in tools currently include:

- Calculator
- Current local time
- Directory listing
- File information
- Text-file reading
- Text-file writing
- Directory creation

The tool framework is fully extensible through the registry architecture.

---

## Agent Foundation

ATLAS currently understands natural-language requests.

The agent can:

- Determine whether a registered tool is required
- Select one appropriate tool
- Generate structured tool arguments
- Validate arguments
- Apply permission policies
- Request confirmation for protected actions
- Execute approved tools
- Generate trusted responses from verified tool results

Current limitations:

- One model-selected tool per request
- No autonomous multi-step planning
- No web research
- No semantic memory retrieval
- No background task execution

These capabilities are intentionally deferred until future releases.

---

## Security

ATLAS follows a least-privilege design philosophy.

Current protections include:

- Registered tools only
- JSON-schema validation
- Permission evaluation
- Confirmation workflow
- Scoped filesystem access
- Path-traversal protection
- Structured audit logging
- Explicit tool registration
- No unrestricted shell execution

---

# Architecture at a Glance

Current architecture:

```text
                 User
                   │
                   ▼
              AtlasApp
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
Command Processing      Agent Pipeline
                              │
                              ▼
                   Structured Decision
                              │
                              ▼
                    Permission System
                              │
                              ▼
                     Tool Execution
                              │
                              ▼
                  Trusted Tool Results
                              │
                              ▼
                      User Response
```

Supporting subsystems:

- Provider layer
- Memory subsystem
- Conversation subsystem
- Logging subsystem
- Tool framework
- Filesystem subsystem
- Permission subsystem
- Agent subsystem

Detailed implementation:

- `ARCHITECTURE.md`

---

# Repository Structure

```text
Project-ATLAS/
│
├── src/
│   └── atlas/
│       ├── agent/
│       ├── conversations/
│       ├── filesystem/
│       ├── memory/
│       ├── models/
│       ├── observability/
│       ├── permissions/
│       ├── tools/
│       └── core/
│
├── docs/
│
├── tests/
│
├── workspace/
│
├── ROADMAP.md
├── CHANGELOG.md
├── ARCHITECTURE.md
└── README.md
```

---

# Current Status

| Component | Status |
|------------|--------|
| Foundation | ✅ Complete |
| AI Providers | ✅ Complete |
| Local AI | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversations | ✅ Complete |
| Structured Logging | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permission System | ✅ Complete |
| Secure Filesystem | ✅ Complete |
| Agent Foundation | ✅ Complete |
| Response Performance | 🚧 Next |
| Web Research | ⏳ Planned |
| Multi-Step Agent | ⏳ Planned |
| Semantic Memory | ⏳ Planned |
| Project Intelligence | ⏳ Planned |

Current Release:

**v1.0.0 — Agent Foundation**

Next Milestone:

**v1.1.0 — Response Performance**

---

# Installation

Clone the repository:

```bash
git clone https://github.com/victoriajarocki/Project-ATLAS.git
cd Project-ATLAS
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install ATLAS:

```bash
pip install -e .
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

---

# Configuration

ATLAS uses a `.env` file for runtime configuration.

Example:

```text
ATLAS_PROVIDER=ollama

OLLAMA_MODEL=qwen3:4b

OLLAMA_HOST=http://localhost:11434

LOG_LEVEL=INFO

MEMORY_DATABASE=data/memory.db

WORKSPACE_DIRECTORY=workspace
```

Additional configuration options are documented in:

- `docs/configuration.md`

---

# Running ATLAS

Launch the application:

```bash
python main.py
```

Example session:

```text
You:
What files are in my workspace?

ATLAS:
Your workspace contains two files:
- .gitkeep
- notes.txt
```

The agent automatically decides whether a registered tool is required to satisfy a request.

Explicit tool commands remain available for development and testing.

---

# Examples

## General Conversation

```text
You:
Explain Newton's Second Law.

ATLAS:
Newton's Second Law states that the net force acting on an object equals its mass multiplied by its acceleration:

F = ma

This means an object's acceleration depends on both the applied force and its mass...
```

---

## Calculator

```text
You:
What is (347 × 982) + 51?

ATLAS:
347 multiplied by 982 equals 340754.

Adding 51 gives:

340805
```

---

## Workspace Inspection

```text
You:
What files are in my workspace?

ATLAS:
Your workspace contains:

• .gitkeep
• notes.txt
• rocket-data.csv
```

---

## Reading Files

```text
You:
Read notes.txt

ATLAS:
The file "notes.txt" contains:

Project Wraith
Launch Checklist
Recovery System
```

---

## Permission Workflow

```text
You:
Create a folder called Flight Data.

ATLAS:
Tool create_directory requires confirmation.

Use:

confirm yes

or

confirm no
```

```text
You:
confirm yes

ATLAS:
Successfully created the directory:

Flight Data
```

---

## Natural Language Agent

```text
You:
Make a folder called Rocket Logs.

ATLAS:
Tool create_directory requires confirmation.
```

```text
You:
confirm yes

ATLAS:
Successfully created:

Rocket Logs
```

The user never needs to explicitly specify which tool should be used.

---

# Safety Model

ATLAS is intentionally conservative.

Every potentially destructive action must pass through multiple safety layers before execution.

Current protection layers include:

1. Natural-language parsing
2. Structured decision validation
3. Tool registration
4. JSON-schema argument validation
5. Permission evaluation
6. User confirmation (when required)
7. Tool execution
8. Structured audit logging

High-risk operations are intentionally unsupported.

Current examples include:

- unrestricted shell execution
- unrestricted filesystem access
- arbitrary Python execution
- unrestricted network access
- desktop automation
- operating-system modification

These capabilities will only be introduced after appropriate safety architecture exists.

---

# Development Philosophy

Project ATLAS follows several engineering principles.

## Architecture First

Stable architecture is prioritized over rapid feature growth.

Infrastructure should exist before advanced capabilities are added.

---

## Modular Design

Every subsystem should be independently testable and replaceable.

Examples include:

- model providers
- memory
- conversations
- logging
- tools
- permissions
- filesystem
- agent

---

## Local First

Whenever practical, ATLAS should continue operating without cloud services.

Local execution provides:

- privacy
- lower operating cost
- developer control
- offline capability

Cloud providers remain optional rather than required.

---

## Explicit User Control

ATLAS should never silently perform meaningful actions.

Users remain responsible for approving protected operations.

---

## Incremental Development

Each release introduces one primary capability.

Every release should leave the project in a stable, releasable state.

---

# Development Workflow

Typical development workflow:

```text
Implement Feature
        ↓
Unit Tests
        ↓
Integration Tests
        ↓
Manual Testing
        ↓
Documentation
        ↓
Changelog
        ↓
Release
```

Before every release:

```bash
ruff check .

ruff format .

mypy src

pytest
```

Current release:

**204 passing automated tests**

---

# Documentation

| Document | Purpose |
|----------|---------|
| README.md | Project overview |
| ARCHITECTURE.md | System architecture |
| ROADMAP.md | Development roadmap |
| CHANGELOG.md | Release history |
| docs/agent.md | Agent subsystem |
| docs/tools.md | Tool framework |
| docs/filesystem.md | Filesystem subsystem |
| docs/permissions.md | Permission system |
| docs/configuration.md | Configuration guide |
| docs/development.md | Development workflow |
| docs/vision.md | Long-term vision |
| docs/future_backlog.md | Long-term ideas and future capabilities |

---

# Roadmap Summary

Current release:

✅ **v1.0.0 — Agent Foundation**

Current development:

🚧 **v1.1.0 — Response Performance**

Near-term roadmap:

- v1.2.0 — Web Research Foundation
- v1.3.0 — Multi-Step Agent and Verification
- v1.4.0 — Semantic Memory
- v1.5.0 — Project Intelligence

Long-term capability areas include:

- Engineering assistance
- Scientific computing
- Desktop automation
- Voice interaction
- Vision
- Manufacturing assistance
- Rocket engineering
- Spatial interfaces
- Robotics

For the complete roadmap:

- `ROADMAP.md`

For the long-term project mission:

- `docs/vision.md`

For future ideas:

- `docs/future_backlog.md`

---

# Contributing

Project ATLAS is currently developed as a long-term personal engineering project.

As the architecture matures, external contributions may be accepted.

Future contribution guidelines will include:

- coding standards
- testing requirements
- documentation requirements
- architectural review
- security review

---

# License

Project ATLAS is released under the MIT License.

See:

`LICENSE`

---

# Acknowledgements

Project ATLAS is built using the Python ecosystem together with several outstanding open-source projects, including:

- Python
- Ollama
- Ruff
- MyPy
- Pytest
- SQLite

Their tools make modern software engineering significantly more productive.

---

# Long-Term Goal

The purpose of Project ATLAS is not simply to build another conversational AI.

The goal is to create a trustworthy, modular, local-first intelligence platform that can grow alongside its user for years.

Future versions aim to assist with:

- engineering
- programming
- research
- scientific computing
- project management
- manufacturing
- rocketry
- knowledge management
- automation
- voice interaction
- visual understanding

Every release is intended to move deliberately toward that vision while maintaining stability, transparency, user control, and strong software-engineering practices.

---

<p align="center">

**Project ATLAS**

*A modular, local-first AI operating system and lifelong engineering partner.*

Current Release: **v1.0.0 — Agent Foundation**

Next Milestone: **v1.1.0 — Response Performance**

</p>