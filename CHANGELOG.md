# Changelog

All notable changes to Project ATLAS will be documented in this file.

The project follows semantic versioning:

- Major version: incompatible architectural changes
- Minor version: new backward-compatible capabilities
- Patch version: backward-compatible fixes

---

## [Unreleased]

### Planned

- Permission and action-confirmation system
- Medium-risk tool approval flow
- File and application tools
- Model-directed tool selection
- Automatic conversation titles
- Semantic memory retrieval

### Added

- GitHub Actions continuous-integration workflow
- Automated Ruff lint checks on pushes and pull requests
- Automated Ruff formatting verification
- Automated mypy static type checks
- Automated pytest test execution

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

- Tool execution currently requires explicit CLI commands.
- Model-directed tool selection is planned for a later version.
- File-system, terminal, and computer-control tools are intentionally deferred until permission and confirmation controls are implemented.

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

- Default logs are stored in `logs/atlas.log`.
- Default log level is `INFO`.
- Log files rotate after approximately 5 MB.
- Five rotated log backups are retained by default.

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

- ATLAS currently sends up to 20 recent messages as context.
- Automatic summarization and token-aware context limits are planned for a later version.
- Explicit persistent memories remain separate from conversation history.

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

- Memory retrieval currently uses recent-memory context and basic text search.
- Semantic vector retrieval is reserved for a later version.
- Conversation sessions and automatic conversation context are reserved for v0.5.0.

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

- Mock remains the default development provider.
- OpenAI support remains available.
- Ollama enables completely local inference.
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

- Mock is the default development provider.
- OpenAI integration is available but requires separate API billing and quota.

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
- Project README