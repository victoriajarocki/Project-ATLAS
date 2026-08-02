# Project ATLAS Roadmap

Project ATLAS is a long-term software engineering project focused on building a modular, local-first AI operating system.

Development follows semantic versioning. Each release introduces a focused capability while preserving architectural stability, backward compatibility, security boundaries, testing, and documentation.

The roadmap below reflects completed milestones and the planned evolution of the platform.

---

# Current Version

**Project ATLAS v1.0.0 — Agent Foundation**

Current development status:

| Component | Status |
|---|---|
| Foundation | ✅ Complete |
| AI Provider Architecture | ✅ Complete |
| Local AI Support | ✅ Complete |
| Persistent Memory | ✅ Complete |
| Conversation Engine | ✅ Complete |
| Structured Logging | ✅ Complete |
| Tool Framework | ✅ Complete |
| Permission System | ✅ Complete |
| Secure Filesystem | ✅ Complete |
| Agent Foundation | ✅ Complete |
| Multi-Step Agent Loop | ⏳ Planned |
| Web Research | ⏳ Planned |
| Semantic Memory | ⏳ Planned |
| Code Execution | ⏳ Planned |
| Desktop Automation | ⏳ Planned |
| Voice Interface | ⏳ Planned |
| Vision System | ⏳ Planned |
| Robotics Platform | ⏳ Long-Term |

---

# Completed Milestones

## v0.1.0 — Foundation

Completed:

- Python project structure
- Package architecture
- Command-line interface
- Development environment
- Automated testing
- Ruff linting and formatting
- MyPy static type checking
- Git version control
- Initial documentation

Status:

✅ Complete

---

## v0.2.0 — AI Provider Architecture

Completed:

- Model-provider abstraction
- Mock provider
- OpenAI provider
- Provider factory
- Environment-based configuration
- Model-provider tests

Status:

✅ Complete

---

## v0.3.0 — Local AI

Completed:

- Ollama integration
- Local model execution
- Local-provider configuration
- Offline development workflow
- Local-model tests

Status:

✅ Complete

---

## v0.4.0 — Persistent Memory

Completed:

- SQLite memory database
- Memory records and IDs
- Remember command
- Forget command
- Memory listing
- Context injection
- Source tracking
- Memory tests

Status:

✅ Complete

---

## v0.5.0 — Conversation Engine

Completed:

- Multiple persistent conversations
- Conversation IDs and titles
- Conversation history
- Conversation switching
- Conversation renaming
- Automatic active-conversation restoration
- Context reconstruction
- Conversation tests

Status:

✅ Complete

---

## v0.6.0 — Structured Logging

Completed:

- Request IDs
- Rotating log files
- Performance timing
- Startup diagnostics
- Error logging
- Memory audit logging
- Conversation audit logging
- Configurable logging
- Logging tests

Status:

✅ Complete

---

## v0.7.0 — Tool Framework

Completed:

- Tool interface
- Tool definitions
- JSON parameter schemas
- Tool registry
- Tool executor
- Structured tool results
- Risk metadata
- Calculator tool
- Current-time tool
- Explicit tool commands
- Tool execution tests

Status:

✅ Complete

---

## v0.8.0 — Permission System

Completed:

- Permission decision models
- Permission policy
- Allow, confirm, and deny decisions
- Risk classification
- Confirmation workflow
- Pending tool requests
- Confirmation commands
- Permission audit logging
- Confirmation tests

Status:

✅ Complete

---

## v0.9.0 — Secure Filesystem

Completed:

- Scoped filesystem subsystem
- Workspace sandbox
- Secure path resolver
- Configurable allowed directories
- Directory listing
- File metadata inspection
- UTF-8 text reading
- UTF-8 text writing
- Directory creation
- Read and write limits
- Path-traversal protection
- Filesystem integration tests
- Filesystem documentation

Status:

✅ Complete

---

## v1.0.0 — Agent Foundation

Objective:

Transform ATLAS from a command-driven assistant into a constrained, tool-using AI agent.

Completed:

- Dedicated agent package
- Agent decision models
- Structured agent-response parser
- Dynamic tool catalog
- Dynamic agent prompt generation
- Structured model decisions
- Natural-language tool selection
- JSON-schema-constrained Ollama decisions
- Agent orchestration service
- Permission-system integration
- Tool-executor integration
- Conversation-context integration
- Persistent-memory context integration
- Model-selected confirmation workflow
- Pending agent tool requests
- Approval and denial handling
- Trusted tool-result responses
- Deterministic file-creation routing
- Deterministic directory-creation routing
- User-friendly local-time output
- Backward-compatible explicit tool commands
- Application-level agent integration
- Agent unit tests
- Agent integration tests
- 204 passing automated tests
- Agent documentation

Current execution model:

```text
User Request
    ↓
AtlasApp
    ↓
Command Detection
    ↓
Deterministic Safety Routing
    ↓
Agent Prompt Builder
    ↓
Structured Model Decision
    ↓
Decision Parser
    ↓
Tool and Argument Validation
    ↓
Permission Evaluation
    ↓
Execution or Confirmation
    ↓
Trusted Tool Result
    ↓
Conversation Storage
    ↓
User Response
```

Current limitations:

- One model-selected tool per request
- No autonomous multi-step loop
- No background execution
- No persistent plans
- No unrestricted shell access
- No unrestricted filesystem access
- Deterministic routing currently targets recognized English file and folder creation requests

Status:

✅ Complete

---

# Next Milestone

## v1.1.0 — Multi-Step Agent Loop

Objective:

Expand ATLAS from single-tool decisions into bounded, multi-step task execution.

Planned capabilities:

- Multi-step agent loop
- Configurable maximum step count
- Sequential tool execution
- Tool-result observation
- Replanning after each tool result
- Final task-completion response
- Agent-loop audit logging
- Loop cancellation
- Failed-tool recovery
- Repeated confirmation handling
- Duplicate-action protection
- Agent-loop integration tests

Example:

```text
User:

Create a folder called Rockets,
create notes.txt inside it,
and write Project Wraith into the file.
```

Planned execution:

```text
Interpret Request
    ↓
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

Safety requirements:

- Hard maximum step count
- Registered tools only
- Validation before every step
- Permission evaluation before every step
- Confirmation for every medium-risk action
- High-risk denial
- No silent continuation after denial
- No repeated execution of completed steps
- Clear cancellation behavior
- Complete integration coverage

Estimated impact:

★★★★★

This milestone will introduce ATLAS's first bounded planning loop without enabling unrestricted autonomy.

---

# Planned Roadmap

## v1.2.0 — Web Research

Planned features:

- Web search tool
- Source retrieval
- Source citations
- Multi-source summarization
- Engineering research workflows
- Technical-documentation retrieval
- Research-result validation
- Trusted-domain controls
- Research audit logging

---

## v1.3.0 — Semantic Memory

Planned features:

- Embedding database
- Vector-based similarity search
- Memory relevance ranking
- Context prioritization
- Source-aware retrieval
- Memory consolidation
- Duplicate-memory detection
- Semantic-memory tests

---

## v1.4.0 — Code Execution

Planned features:

- Sandboxed Python execution
- Resource limits
- Time limits
- Safe file handoff
- Engineering calculations
- Data analysis
- Plot generation
- Structured execution results
- Code-execution permissions

---

## v1.5.0 — Desktop Automation

Planned features:

- Application launching
- Window discovery
- Keyboard control
- Mouse control
- File interaction
- Desktop workflows
- Screenshot-based state verification
- Strong confirmation requirements
- Restricted application allowlists

---

## v1.6.0 — Voice Interface

Planned features:

- Speech recognition
- Speech synthesis
- Streaming conversations
- Wake-word detection
- Push-to-talk mode
- Interruption handling
- Local speech options
- Voice-session logging controls

---

## v2.0.0 — Vision System

Planned features:

- Image understanding
- Screenshot analysis
- OCR
- Camera support
- Visual tool selection
- Multimodal reasoning
- Visual-context memory
- Vision-specific safety controls

---

## v2.1.0 — Personal Knowledge System

Planned features:

- Document indexing
- PDF understanding
- Local document search
- Personal knowledge graph
- Workspace organization
- Source-linked answers
- Document metadata
- Knowledge synchronization

---

## v2.2.0 — Engineering Assistant

Planned features:

- Python engineering workflows
- MATLAB integration
- CAD assistance
- Simulation support
- Scientific computing
- Unit-aware calculations
- Engineering-document interpretation
- Domain-specific tool plugins

---

## v2.3.0 — Automation and Scheduling

Planned features:

- Scheduled tasks
- Recurring workflows
- Conditional monitoring
- Task history
- Notification policies
- Retry controls
- User-defined automation rules
- Persistent automation state

---

## v3.0.0 — AI Operating System

Long-term objective:

Create a modular AI operating system capable of coordinating every subsystem through bounded autonomous reasoning.

Major goals:

- Unified planning engine
- Autonomous workflow execution
- Long-term adaptive memory
- Voice-first interaction
- Vision integration
- Desktop automation
- Engineering assistance
- Personal knowledge integration
- Plugin ecosystem
- Robotics coordination
- Strong user authorization
- Complete local-first operation where practical

---

# Long-Term Robotics Roadmap

Future robotics development may include:

- Sensor integration
- Real-time state monitoring
- Robot-control APIs
- Embedded-device communication
- Motion planning
- Safety interlocks
- Physical authorization boundaries
- Simulation-first testing
- Autonomous navigation
- Real-world task execution

Robotics capabilities will require substantially stronger safety, testing, and authorization controls than software-only tools.

---

# Long-Term Vision

Project ATLAS is intended to become a modular AI platform capable of supporting years of continued development.

Rather than optimizing for rapid feature growth, every release prioritizes:

- Stable architecture
- Modular design
- Local-first operation
- Privacy
- Explicit permissions
- Extensibility
- Testing
- Documentation
- Maintainability
- Safe failure behavior

Each subsystem is developed independently while integrating into a unified AI operating system.

---

# Development Principles

Every release follows the same engineering philosophy:

- One focused capability per milestone
- Backward-compatible evolution where practical
- Comprehensive automated testing
- Architecture-first design
- Explicit security boundaries
- Thorough documentation
- Versioned releases
- Continuous integration
- Manual acceptance testing
- Clear deferred scope

This incremental approach ensures ATLAS remains maintainable as it grows from a command-line assistant into a complete AI operating system.

---

# Release Sequence

| Version | Milestone | Status |
|---|---|---|
| v0.1.0 | Foundation | ✅ Complete |
| v0.2.0 | AI Provider Architecture | ✅ Complete |
| v0.3.0 | Local AI | ✅ Complete |
| v0.4.0 | Persistent Memory | ✅ Complete |
| v0.5.0 | Conversation Engine | ✅ Complete |
| v0.6.0 | Structured Logging | ✅ Complete |
| v0.7.0 | Tool Framework | ✅ Complete |
| v0.8.0 | Permission System | ✅ Complete |
| v0.9.0 | Secure Filesystem | ✅ Complete |
| v1.0.0 | Agent Foundation | ✅ Complete |
| v1.1.0 | Multi-Step Agent Loop | ⏳ Planned |
| v1.2.0 | Web Research | ⏳ Planned |
| v1.3.0 | Semantic Memory | ⏳ Planned |
| v1.4.0 | Code Execution | ⏳ Planned |
| v1.5.0 | Desktop Automation | ⏳ Planned |
| v1.6.0 | Voice Interface | ⏳ Planned |
| v2.0.0 | Vision System | ⏳ Planned |
| v2.1.0 | Personal Knowledge System | ⏳ Planned |
| v2.2.0 | Engineering Assistant | ⏳ Planned |
| v2.3.0 | Automation and Scheduling | ⏳ Planned |
| v3.0.0 | AI Operating System | ⏳ Long-Term |

---

**Current Release:** **v1.0.0 — Agent Foundation**

**Next Milestone:** **v1.1.0 — Multi-Step Agent Loop**