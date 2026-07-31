# Changelog

All notable changes to Project ATLAS will be documented in this file.

The project follows semantic versioning:

- Major version: incompatible architectural changes
- Minor version: new backward-compatible capabilities
- Patch version: backward-compatible fixes

---

## [Unreleased]

### Planned

- Persistent conversation sessions
- Multi-message model context
- Conversation summaries
- Structured logging
- Semantic memory retrieval
- Memory editing and categorization commands

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