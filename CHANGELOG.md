# Changelog

All notable changes to Project ATLAS will be documented in this file.

The project follows semantic versioning:

- Major version: incompatible architectural changes
- Minor version: new backward-compatible capabilities
- Patch version: backward-compatible fixes

---

## [Unreleased]

### Planned

- Long-term memory engine
- Conversation history
- Session management
- Structured logging
- SQLite memory database
- Semantic memory retrieval
- User profile management

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