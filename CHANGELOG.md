# Changelog

All notable changes to Project ATLAS will be documented in this file.

The project follows semantic versioning:

- Major version: incompatible architectural changes
- Minor version: new backward-compatible capabilities
- Patch version: backward-compatible fixes

## [Unreleased]

### Planned

- Add local Ollama model provider
- Add conversation history
- Add structured logging
- Add session management

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