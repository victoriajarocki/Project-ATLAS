# Project ATLAS Development Guide

This guide defines the development workflow and code-quality expectations for Project ATLAS.

ATLAS is intended to become a long-lived software platform. New features should therefore preserve modularity, reliability, testability, privacy, and maintainability.

---

## Development Principles

All contributions should follow these principles:

- Keep subsystems modular.
- Add type hints to functions and methods.
- Include meaningful docstrings.
- Avoid placing secrets in source code.
- Add tests for new behavior.
- Log important operations without exposing sensitive content.
- Use interfaces for replaceable implementations.
- Keep user data local unless an external service is explicitly selected.
- Update documentation alongside code.
- Update `CHANGELOG.md` for every version release.

---

## Development Environment

Create and activate the virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install ATLAS in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

---

## Branch Workflow

Development should take place on a dedicated branch rather than directly on `main`.

Start from the latest primary branch:

```powershell
git switch main
git pull
```

Create a feature branch:

```powershell
git switch -c feature/descriptive-feature-name
```

Examples:

```text
feature/permission-system
feature/filesystem-tools
feature/voice-interface
docs/developer-documentation
fix/ollama-connection-error
```

View the current branch:

```powershell
git branch --show-current
```

---

## Development Cycle

A normal feature cycle is:

```text
Create branch
    ↓
Implement feature
    ↓
Add or update tests
    ↓
Run quality checks
    ↓
Update documentation
    ↓
Update CHANGELOG.md
    ↓
Commit
    ↓
Push
    ↓
Merge
```

---

## Code Style

### Module Docstrings

Every Python module should begin with a short module docstring:

```python
"""Tool registration and discovery for Project ATLAS."""
```

### Function and Method Docstrings

Public functions and methods should explain their purpose:

```python
def register(self, tool: Tool) -> None:
    """Register a tool by its unique name."""
```

### Type Hints

Use type hints for parameters and return values:

```python
def process_message(self, user_message: str) -> str:
    """Process one user message."""
```

Avoid untyped functions unless a library integration makes typing impractical.

### Line Length

The project uses a maximum line length of 100 characters, configured through Ruff.

### Imports

Imports should be grouped and ordered automatically by Ruff:

1. Python standard library
2. Third-party packages
3. ATLAS modules

Run:

```powershell
ruff check . --fix
```

to correct import ordering and other safe issues.

---

## Formatting

Format the project:

```powershell
ruff format .
```

Verify that no formatting changes are required:

```powershell
ruff format --check .
```

Do not manually fight the formatter. Format the project and commit the standardized output.

---

## Linting

Run:

```powershell
ruff check .
```

Apply automatically fixable changes:

```powershell
ruff check . --fix
```

After applying fixes, verify again:

```powershell
ruff check .
```

---

## Static Type Checking

Run:

```powershell
mypy src
```

ATLAS uses strict type checking. New code should not introduce ignored typing errors without a documented reason.

A successful result resembles:

```text
Success: no issues found
```

---

## Testing

Run the entire test suite:

```powershell
pytest
```

Run a specific test file:

```powershell
pytest tests\test_tools.py
```

Run one test:

```powershell
pytest tests\test_tools.py::test_calculator_addition
```

Display more detail:

```powershell
pytest -v
```

New functionality should include tests for:

- Normal behavior
- Invalid input
- Boundary conditions
- Failure handling
- Security-sensitive behavior
- Persistence, when applicable

Tests that use databases should use temporary test paths rather than the real ATLAS database.

---

## Complete Local Quality Check

Before committing, run:

```powershell
ruff check .
ruff format --check .
mypy src
pytest
```

Do not release a version while any check is failing.

---

## Git Status and Diffs

View changed files:

```powershell
git status
```

View unstaged changes:

```powershell
git diff
```

View staged changes:

```powershell
git diff --staged
```

Stage changes:

```powershell
git add .
```

Review the staged changes before committing:

```powershell
git status
git diff --staged
```

---

## Commit Messages

Commit messages should be short, specific, and written in the imperative or release style.

Examples:

```text
Add permission policy evaluator
Fix Ollama response validation
Document tool framework
Release ATLAS v0.8.0 permissions system
```

Avoid vague messages such as:

```text
updates
changes
stuff
fixed code
```

Create a commit:

```powershell
git commit -m "Add permission policy evaluator"
```

---

## Pushing to GitHub

Push a new branch and configure its upstream:

```powershell
git push -u origin feature/descriptive-feature-name
```

After the upstream is configured:

```powershell
git push
```

---

## Merging a Completed Feature

After reviewing and testing the feature:

```powershell
git switch main
git pull
git merge feature/descriptive-feature-name
git push origin main
```

Delete the completed local branch:

```powershell
git branch -d feature/descriptive-feature-name
```

A GitHub pull request may be used instead of a local merge.

---

## Version Releases

Every release should update:

- `pyproject.toml`
- `src/atlas/main.py`
- `tests/test_main.py`
- `CHANGELOG.md`
- `README.md`, when the displayed version or capabilities change
- `ROADMAP.md`, when milestone status changes
- Relevant files inside `docs/`

Release checklist:

```text
[ ] Feature is complete
[ ] Tests are added
[ ] Ruff passes
[ ] Formatting passes
[ ] mypy passes
[ ] pytest passes
[ ] Manual test passes
[ ] Version numbers match
[ ] CHANGELOG.md is updated
[ ] Documentation is updated
[ ] Sensitive files remain ignored
[ ] Release commit is pushed
```

---

## Adding a New Subsystem

A new subsystem should generally use this structure:

```text
src/atlas/subsystem/
├── __init__.py
├── models.py
├── service.py
└── database.py
```

Not every subsystem needs every file. The structure should reflect actual responsibilities rather than forcing unnecessary layers.

Typical responsibilities:

- `models.py` — dataclasses and domain records
- `service.py` — validation and business logic
- `database.py` — persistence
- `__init__.py` — exported public interface

---

## Adding a New Model Provider

A model provider must implement the `ModelProvider` interface.

Required behavior:

```python
class ExampleModelProvider(ModelProvider):
    @property
    def provider_name(self) -> str:
        """Return the provider name."""

    def generate_response(self, user_message: str) -> str:
        """Generate a model response."""
```

Then:

1. Add the provider module.
2. Extend the provider factory.
3. Extend configuration if necessary.
4. Add unit tests.
5. Update `.env.example`.
6. Update documentation and the changelog.

---

## Adding a New Tool

A tool must implement the `Tool` interface.

Each tool must provide:

- A unique name
- A description
- A parameter schema
- A risk classification
- Confirmation metadata
- Input validation
- A structured `ToolResult`

See [Tool System](tools.md) for the complete tool-development workflow.

---

## Logging Rules

Log operational information such as:

- Request IDs
- Component names
- Tool names
- Record IDs
- Durations
- Success or failure

Do not log:

- API keys
- Full user messages
- Memory contents
- Conversation contents
- Passwords
- Private tokens
- Unnecessary personal data

---

## Security Rules

Never commit:

```text
.env
API keys
passwords
tokens
local databases
private logs
```

Before pushing, verify:

```powershell
git check-ignore .env
git check-ignore data\atlas_memory.db
git check-ignore logs\atlas.log
```

If a secret is accidentally committed, removing it from the current file is not sufficient. The secret must be revoked and removed from Git history.

---

## Documentation Rules

Documentation should describe the behavior that actually exists.

When implementation changes:

- Update the relevant document.
- Remove outdated claims.
- Update examples.
- Update the current-version information.
- Record the release in `CHANGELOG.md`.

The changelog records completed work. The roadmap records planned work.

## Continuous Integration

Project ATLAS uses GitHub Actions to run automated quality checks.

The workflow is defined in:

```text
.github/workflows/ci.yml
```

It runs when:

- Code is pushed to `master`
- A pull request targets `master`
- The workflow is started manually

The workflow verifies:

```powershell
ruff check .
ruff format --check .
mypy src
pytest
```

A pull request should not be merged while required CI checks are failing.

Local checks should still be run before pushing because CI is a final verification step rather than a replacement for local development testing.

---

## Definition of Done

A feature is complete only when:

1. The implementation works.
2. Tests cover the new behavior.
3. Static checks pass.
4. Errors are handled.
5. Security implications are considered.
6. Logs are appropriate.
7. Documentation is updated.
8. `CHANGELOG.md` is updated for a release.
9. The feature is committed and pushed.