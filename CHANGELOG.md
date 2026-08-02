# Changelog

All notable changes to Project ATLAS are documented in this file.

The project follows semantic versioning:

- Major version: incompatible architectural changes
- Minor version: new backward-compatible capabilities
- Patch version: backward-compatible fixes

---

## [Unreleased]

### Planned

- Multi-step agent execution
- Replanning after tool results
- Agent step limits
- Automatic conversation titles
- Semantic memory retrieval
- Web research tools
- Improved deterministic action routing
- Better user-facing tool-result formatting

---

## [1.0.0] - 2026-08-01

### Added

- Dedicated agent subsystem
- Agent decision models
- Agent decision types
- Structured tool-request models
- Agent pending-request models
- Agent run-result models
- Agent-specific exceptions
- Structured agent-response parser
- Strict JSON-object validation
- Unknown-field rejection
- Dynamic agent prompt builder
- Dynamic registered-tool catalog
- Tool parameter schemas in agent prompts
- Tool risk metadata in agent prompts
- Structured-output contract for model decisions
- Agent orchestration service
- Natural-language tool selection
- Direct-response decisions
- Model-selected tool-use decisions
- Agent integration with the permission system
- Agent integration with the tool executor
- Agent integration with conversation context
- Agent integration with persistent memory context
- Agent-selected confirmation workflow
- Pending model-selected tool requests
- Confirmation approval for agent-selected tools
- Confirmation denial for agent-selected tools
- Application-level agent integration
- Agent-enabled startup status
- Natural-language calculator selection
- Natural-language current-time selection
- Natural-language directory listing
- Natural-language file reading
- Natural-language directory creation
- Natural-language file creation
- Deterministic routing for recognized file-creation requests
- Deterministic routing for recognized directory-creation requests
- Structured-output model-provider interface
- Ollama JSON-schema-constrained responses
- Ollama thinking suppression
- Ollama model keep-alive configuration
- Ollama output-length limits
- Defensive cleanup for leaked reasoning blocks
- User-friendly local date-and-time formatting
- Agent unit tests
- Agent parser tests
- Agent prompt tests
- Agent service tests
- Agent application integration tests
- Deterministic routing tests
- Agent confirmation tests
- Agent history-persistence tests
- Agent documentation

### Changed

- Normal user messages now pass through the agent subsystem when enabled
- ATLAS can now decide whether to answer directly or use one registered tool
- Registered tools are exposed dynamically to the model
- Agent decisions now use a strict JSON structure
- Ollama decisions now use native JSON-schema-constrained output
- Tool requests selected by the model now pass through shared argument validation
- Tool requests selected by the model now pass through permission evaluation
- Medium-risk model-selected tools now pause for confirmation
- High-risk model-selected tools remain denied
- Approved model-selected tools now resume through the existing confirmation workflow
- Explicit `tool ...` commands remain supported
- Explicit and model-selected tools now share the same registry, validator, permission service, and executor
- Tool-assisted agent requests now return trusted tool output directly
- The second model call after tool execution was removed
- Tool-assisted response latency was reduced
- Reasoning-output leakage was prevented from reaching the user
- Recognized file and folder creation requests bypass model discretion
- Conversation history now stores final agent responses
- The command-line startup display now reports agent availability
- The current-time tool now returns a readable local date, time, and timezone
- The project version is now 1.0.0
- The automated test suite now contains 204 passing tests

### Security

- The agent may select only registered tools
- Tool arguments must match registered parameter schemas
- Invalid structured decisions are rejected
- Invalid JSON model output is rejected
- Unknown decision fields are rejected
- Unknown tool-request fields are rejected
- Hallucinated tool names are rejected
- Invalid model-generated tool arguments are rejected
- Medium-risk actions require explicit user confirmation
- High-risk actions remain denied by default
- Pending actions block unrelated requests
- Recognized file and directory creation requests are routed deterministically
- The model cannot silently execute filesystem state changes
- Trusted tool output is returned directly after execution
- A second model call cannot rewrite or misrepresent tool results
- Leaked `<think>` blocks are removed from Ollama output
- Filesystem actions remain restricted to configured allowed directories
- Path traversal protections remain active
- Existing-file protections remain active
- Arbitrary shell execution remains unsupported
- Unrestricted filesystem access remains unsupported
- Agent execution is limited to one selected tool per request
- No autonomous background loop is implemented
- No self-modifying prompt behavior is implemented

### Notes

- Version 1.0.0 introduces a constrained single-tool agent foundation
- Multi-step planning is intentionally deferred
- Agent tool decisions depend on the quality of the active model
- Deterministic routing currently covers recognized English file and directory creation requests
- Tool-assisted responses currently return trusted tool output rather than model-rewritten summaries
- Explicit tool commands remain available for debugging and direct control
- Ollama is the recommended local provider for agent testing
- The current recommended local model remains `qwen3:4b`

---

## [0.9.0] - 2026-08-01

### Added

- Secure filesystem subsystem
- Scoped path resolver
- `FileSystemService`
- Configurable workspace directories
- Directory listing tool
- File information tool
- Read text file tool
- Write text file tool
- Create directory tool
- Shared JSON-schema validator
- Filesystem configuration settings
- Filesystem integration tests
- Filesystem documentation

### Changed

- Tool execution now validates arguments before permission evaluation
- `ToolExecutor` now exposes reusable argument validation
- Configuration now supports filesystem settings
- Tool registry now includes filesystem tools
- Updated the command-line interface with filesystem commands
- Updated the project version to 0.9.0

### Security

- Filesystem access is restricted to configured workspace directories
- Path traversal attempts are rejected
- Read and write limits are configurable
- Medium-risk filesystem operations require confirmation
- Read-only filesystem operations execute automatically
- Filesystem activity is recorded through structured logging

### Notes

- Filesystem support currently targets UTF-8 text files
- File deletion and renaming are intentionally deferred
- Future releases will expand filesystem capabilities

---

## [0.8.0] - 2026-08-01

### Added

- Permission decision models
- Permission policy evaluator
- Permission coordination service
- Allow, confirm, and deny decisions
- Confirmation-controlled tool execution
- `confirm yes` command
- `confirm no` command
- Pending tool-request state
- Confirmation demonstration tool
- Permission audit logging
- Confirmation workflow tests
- Permission subsystem documentation

### Changed

- Tool requests now pass through permission evaluation
- Medium-risk tools require explicit approval
- Confirmation-controlled tools pause before execution
- Updated the command-line interface with confirmation commands
- Updated the project version to 0.8.0

### Security

- High-risk tools are denied by default
- Pending requests cannot be silently replaced
- Tool arguments are excluded from permission logs
- Confirmation is required before medium-risk execution
- Permission decisions are fully audited

### Notes

- Permission decisions currently use static tool metadata
- Persistent allow-always permissions are planned for a future release
- Pending requests exist only in process memory

---

## [0.7.0] - 2026-07-31

### Added

- Extensible tool interface
- Tool definitions and parameter schemas
- Tool registry
- Controlled tool executor
- Tool execution results
- Tool risk classifications
- Tool confirmation metadata
- Explicit `tools` command
- Explicit `tool` execution command
- Safe arithmetic calculator tool
- Current local date-and-time tool
- Unit tests for registration, validation, and execution
- Tool execution logging and timing

### Changed

- Extended ATLAS Core with an optional tool subsystem
- Updated the command-line interface with tool commands
- Updated the application startup process to register built-in tools
- Updated the project version to 0.7.0

### Security

- Calculator expressions are parsed through a restricted syntax tree
- Python `eval()` is not used
- Arbitrary imports and function calls are rejected
- Only explicitly registered tools can be executed
- Initial tools are classified as low risk
- Tool logs exclude complete user arguments

### Notes

- Tool execution currently requires explicit CLI commands
- Model-directed tool selection is planned for a later version
- Filesystem, terminal, and computer-control tools were intentionally deferred until permission and confirmation controls were implemented

---

## [0.6.0] - 2026-07-31

### Added

- Structured application logging
- Rotating local log files
- Unique request IDs
- Request-scoped log context
- Request execution timing
- Model-response completion logs
- Application startup and shutdown logs
- Memory-operation audit entries
- Conversation-operation audit entries
- Configurable log levels
- Configurable log rotation limits
- Unit tests for logging configuration and request context

### Changed

- Extended environment configuration with logging settings
- Added subsystem initialization logs
- Added centralized exception logging
- Updated the project version to 0.6.0

### Security

- Logs remain local and excluded from Git
- Full user messages are not written to application logs
- Memory contents are not written to application logs
- Conversation contents are not written to application logs
- Request identifiers contain no personal information

### Notes

- Default logs are stored in `logs/atlas.log`
- Default log level is `INFO`
- Log files rotate after approximately 5 MB
- Five rotated log backups are retained by default

---

## [0.5.0] - 2026-07-31

### Added

- Persistent conversation sessions
- Conversation IDs and titles
- Persistent user and assistant message history
- Automatic restoration of the most recently active conversation
- `new chat` command
- `chats` command
- `use chat` command
- `rename chat` command
- `history` command
- Multi-message context for model responses
- Conversation repository and service layers
- Unit tests for conversation persistence and context

### Changed

- Extended ATLAS Core with conversation-session coordination
- Combined persistent memory and conversation context for model requests
- Updated the command-line interface with conversation controls
- Updated the project version to 0.5.0

### Security

- Conversation history remains local
- Conversation data remains excluded from Git
- Database queries continue to use parameterized SQL values

### Notes

- ATLAS currently sends up to 20 recent messages as context
- Automatic summarization and token-aware context limits are planned for a later version
- Explicit persistent memories remain separate from conversation history

---

## [0.4.0] - 2026-07-31

### Added

- Persistent SQLite memory database
- Memory records with IDs and timestamps
- Memory categories and source tracking
- Explicit `remember` command
- Explicit `memories` command
- Explicit `forget` command
- Persistent-memory context for model responses
- Memory input validation
- Memory repository and service layers
- Unit tests for persistent storage
- Isolated temporary databases for tests

### Changed

- Extended ATLAS Core with an optional memory subsystem
- Extended environment configuration with a memory database path
- Updated the command-line interface with memory commands
- Updated the project version to 0.4.0

### Security

- Memory database remains local and excluded from Git
- SQL values use parameterized database queries
- ATLAS stores memories only through explicit user commands

### Notes

- Memory retrieval currently uses recent-memory context and basic text search
- Semantic vector retrieval is reserved for a later version
- Conversation sessions and automatic conversation context are reserved for v0.5.0

---

## [0.3.0] - 2026-07-31

### Added

- Ollama model provider
- Local AI inference support
- Ollama configuration options
- Ollama provider unit tests
- Support for local model hosts
- Local development workflow without API costs

### Changed

- Extended the provider factory to support multiple AI backends
- Extended the configuration system with Ollama settings
- Updated the application version to 0.3.0
- Improved provider abstraction for future expansion

### Notes

- Mock remains the default development provider
- OpenAI support remains available
- Ollama enables completely local inference
- Current recommended development model:
  - `qwen3:4b`

---

## [0.2.0] - 2026-07-29

### Added

- Abstract model provider interface
- Mock provider for offline development and testing
- OpenAI model provider
- OpenAI Responses API integration
- Environment-based configuration
- Model provider factory
- ATLAS Core application coordinator
- Unit tests for model providers and ATLAS Core

### Changed

- Refactored the command-line interface
- Replaced hard-coded responses with interchangeable model providers
- Updated the project version to 0.2.0

### Notes

- Mock is the default development provider
- OpenAI integration is available but requires separate API billing and quota

---

## [0.1.0] - 2026-07-29

### Added

- Initial Python project structure
- Command-line interface
- Rule-based response system
- Python virtual environment configuration
- Editable package installation
- Automated testing with pytest
- Linting and formatting with Ruff
- Static type checking with mypy
- Git version control
- Initial project documentation