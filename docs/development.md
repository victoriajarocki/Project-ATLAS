# Project ATLAS Development Guide

This guide defines the development workflow, code-quality expectations, security requirements, and release process for Project ATLAS.

ATLAS is intended to become a long-lived AI operating platform. New features must preserve modularity, reliability, testability, privacy, security, and maintainability.

Version 1.0.0 introduces the first agent subsystem. Agent-related development must follow the same validation, permission, testing, and documentation standards as the rest of the application.

---

## Development Principles

All contributions should follow these principles:

- Keep subsystems modular.
- Give each class and service one clear responsibility.
- Add type hints to functions and methods.
- Include meaningful module, class, and public-method docstrings.
- Avoid placing secrets in source code.
- Add tests for new behavior.
- Add regression tests for fixed bugs.
- Log important operations without exposing sensitive content.
- Use interfaces for replaceable implementations.
- Inject dependencies rather than constructing them inside business logic.
- Keep user data local unless an external service is explicitly selected.
- Validate input before authorization.
- Authorize actions before execution.
- Preserve scoped resource boundaries.
- Update documentation alongside implementation changes.
- Update `CHANGELOG.md` for every release.
- Keep roadmap claims consistent with implemented behavior.
- Never document planned behavior as already complete.

---

## Development Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install ATLAS in editable development mode:

```powershell
python -m pip install -e ".[dev]"
```

Confirm the package is available:

```powershell
python -c "import atlas; print('ATLAS package loaded')"
```

Launch the application:

```powershell
atlas
```

---

## Recommended Local Configuration

For local Ollama development:

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434

OPENAI_API_KEY=

ATLAS_MEMORY_DATABASE=data/atlas_memory.db

ATLAS_LOG_DIRECTORY=logs
ATLAS_LOG_LEVEL=INFO
ATLAS_LOG_MAX_BYTES=5000000
ATLAS_LOG_BACKUP_COUNT=5

ATLAS_ALLOWED_DIRECTORIES=workspace
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

For deterministic infrastructure tests:

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
```

The real `.env` file must remain excluded from Git.

---

## Branch Workflow

Development should take place on a dedicated branch rather than directly on the primary branch.

Project ATLAS currently uses:

```text
master
```

as its primary branch.

Start from the latest primary branch:

```powershell
git switch master
git pull origin master
```

Create a feature branch:

```powershell
git switch -c feature/descriptive-feature-name
```

Examples:

```text
feature/agent-foundation
feature/multi-step-agent
feature/web-research
feature/semantic-memory
docs/developer-documentation
fix/ollama-structured-output
fix/filesystem-error-reporting
```

View the current branch:

```powershell
git branch --show-current
```

View local and remote branches:

```powershell
git branch -a
```

---

## Development Cycle

A normal feature cycle is:

```text
Create branch
    ↓
Define scope
    ↓
Implement feature
    ↓
Add or update tests
    ↓
Run focused tests
    ↓
Run complete quality checks
    ↓
Perform manual acceptance testing
    ↓
Update documentation
    ↓
Update CHANGELOG.md
    ↓
Review Git diff
    ↓
Commit
    ↓
Push
    ↓
Open pull request
    ↓
Pass CI
    ↓
Merge
```

Features should not be merged while required checks are failing.

---

## Repository Structure

Current high-level structure:

```text
Project-ATLAS/
│
├── docs/
│   ├── agent.md
│   ├── configuration.md
│   ├── development.md
│   ├── filesystem.md
│   ├── installation.md
│   ├── permissions.md
│   └── tools.md
│
├── src/
│   └── atlas/
│       ├── agent/
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
├── workspace/
│
├── ARCHITECTURE.md
├── CHANGELOG.md
├── README.md
├── ROADMAP.md
└── pyproject.toml
```

New code should be placed inside the subsystem that owns the behavior.

Avoid placing unrelated logic inside `AtlasApp`.

---

## Code Style

### Module Docstrings

Every Python module should begin with a short module docstring:

```python
"""Tool registration and discovery for Project ATLAS."""
```

### Class Docstrings

Every public class should explain its responsibility:

```python
class ToolRegistry:
    """Register and retrieve ATLAS tools."""
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
def process_message(
    self,
    user_message: str,
) -> str:
    """Process one user message."""
```

Avoid untyped functions unless a third-party integration makes typing impractical.

### Line Length

The project uses a maximum line length of 100 characters, configured through Ruff.

### Imports

Imports should be grouped in this order:

1. Python standard library
2. Third-party packages
3. ATLAS modules

Ruff should manage import ordering.

Run:

```powershell
ruff check . --fix
```

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

Do not manually format code in ways that conflict with Ruff.

Documentation code blocks may also be checked by Ruff when they contain Python examples.

If Ruff reports a documentation formatting issue, update the example to match the formatter's expected style.

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

Then verify again:

```powershell
ruff check .
```

A successful result resembles:

```text
All checks passed!
```

---

## Static Type Checking

Run:

```powershell
mypy src
```

ATLAS uses strict type checking.

New code should not introduce ignored typing errors without a documented reason.

A successful result resembles:

```text
Success: no issues found in 53 source files
```

The exact source-file count may increase as the project grows.

---

## Testing

Run the complete suite:

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

Display detailed output:

```powershell
pytest -v
```

Stop after the first failure:

```powershell
pytest -x
```

Show local variables in failures:

```powershell
pytest -l
```

Current v1.0.0 suite:

```text
204 passing tests
```

The exact count may increase as new regression tests are added.

---

## Test Design Principles

New functionality should include tests for:

- Normal behavior
- Invalid input
- Missing input
- Incorrect types
- Unknown fields
- Boundary conditions
- Failure handling
- Security-sensitive behavior
- Persistence, when applicable
- Logging behavior, when important
- Permission behavior, when tools are involved
- Explicit command behavior
- Natural-language agent behavior
- Backward compatibility

Tests should be isolated and deterministic.

Tests must not depend on:

- The real ATLAS database
- The real workspace
- The real log directory
- A live OpenAI account
- A running Ollama server
- Network access
- User-specific files

Use temporary directories and scripted providers.

---

## Database Testing

Tests that use persistence should use temporary database paths.

Example:

```python
database_path = tmp_path / "atlas_test.db"
```

Do not use:

```text
data/atlas_memory.db
```

inside automated tests.

Test database behavior should include:

- Initialization
- Insertions
- Retrieval
- Updates
- Deletion
- Persistence across service instances
- Invalid identifiers
- Empty state
- Isolation between tests

---

## Filesystem Testing

Filesystem functionality should be tested with pytest temporary directories.

Recommended coverage includes:

- Allowed relative paths
- Allowed absolute paths
- Parent traversal
- Outside-scope paths
- Missing files
- Missing directories
- File-versus-directory validation
- UTF-8 decoding
- Invalid UTF-8
- Read limits
- Write limits
- Overwrite protection
- Existing directories
- Existing files
- Multiple allowed roots

Run filesystem tests:

```powershell
pytest tests\test_filesystem.py
```

Run filesystem tool tests:

```powershell
pytest tests\test_tools.py
```

Run application integration tests:

```powershell
pytest tests\test_app.py
```

---

# Agent Development

The v1.0.0 agent subsystem is located in:

```text
src/atlas/agent/
```

Current files include:

```text
src/atlas/agent/
├── __init__.py
├── exceptions.py
├── models.py
├── parser.py
├── prompt.py
└── service.py
```

Agent development must preserve the current security pipeline.

---

## Agent Execution Pipeline

The current single-tool pipeline is:

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
Model Provider
    ↓
Structured Decision
    ↓
Decision Parser
    ↓
Tool Lookup
    ↓
Argument Validation
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

No agent feature may bypass:

- Tool registration
- Argument validation
- Permission evaluation
- Confirmation requirements
- Tool execution controls
- Filesystem scope enforcement

---

## Agent Prompt Development

Agent prompts are built by:

```text
AgentPromptBuilder
```

Prompt changes should be:

- Explicit
- Minimal
- Testable
- Provider-independent where practical
- Consistent with registered tools
- Consistent with the structured decision schema

Prompt instructions should not claim capabilities ATLAS does not have.

When changing prompts, update:

```text
tests/test_agent_prompt.py
```

Test for:

- Required instructions
- Tool catalog inclusion
- Conversation context
- Current user request
- Raw JSON requirement
- File and folder action rules
- Workspace path behavior
- Current-time behavior
- Calculator selection behavior

Prompt-only safeguards must not be treated as a complete security boundary.

Application-level validation is still required.

---

## Structured Agent Decisions

The model may return either:

```json
{
  "decision": "respond",
  "response": "Direct response text."
}
```

or:

```json
{
  "decision": "use_tool",
  "tool": {
    "name": "calculator",
    "arguments": {
      "expression": "2 + 2"
    }
  }
}
```

Developers must never trust model output directly.

Structured output must pass through:

```text
JSON parsing
    ↓
Decision validation
    ↓
Tool lookup
    ↓
Argument validation
```

The parser must reject:

- Invalid JSON
- Non-object roots
- Unknown decision types
- Missing required fields
- Unknown fields
- Missing tool requests
- Invalid response values
- Invalid argument structures

Update:

```text
tests/test_agent_parser.py
```

whenever the structured contract changes.

---

## Structured Model Providers

The `ModelProvider` interface supports:

```python
def generate_response(
    self,
    user_message: str,
) -> str:
    """Generate a normal model response."""
```

and:

```python
def generate_structured_response(
    self,
    user_message: str,
    schema: dict[str, Any],
) -> str:
    """Generate a response constrained by a JSON schema."""
```

Providers without native structured-output support may use the base fallback.

Providers with native support should override the method.

The Ollama provider currently uses:

- JSON-schema output
- Thinking disabled
- Low temperature
- Output limits
- Model keep-alive
- Defensive reasoning cleanup

Provider changes should include tests in:

```text
tests/test_models.py
```

Do not rely on live network or local model calls in unit tests.

---

## Agent Service Development

`AgentService` coordinates:

- Prompt generation
- Structured model requests
- Decision parsing
- Tool validation
- Permission evaluation
- Tool execution
- Confirmation completion
- Confirmation denial
- Trusted result handling

The agent service should remain an orchestration layer.

Do not move:

- Tool business logic
- Filesystem operations
- Permission-policy rules
- Conversation persistence
- Memory persistence

into `AgentService`.

---

## Deterministic Action Routing

Version 1.0.0 includes deterministic routing for recognized file and directory creation requests.

Examples:

```text
Create a folder called Rocket Design.
```

```text
Create a file called hello.txt that says Hello World.
```

These requests bypass model discretion and become structured tool requests.

Deterministic routing exists to prevent false model claims that state-changing actions already occurred.

When modifying deterministic routing:

- Keep patterns narrowly scoped.
- Avoid interpreting ambiguous requests.
- Preserve permission evaluation.
- Preserve argument validation.
- Preserve confirmation.
- Add positive tests.
- Add negative tests.
- Test punctuation and spacing.
- Test quoted values.
- Test that the model is not called.
- Test that execution does not occur before confirmation.

Relevant tests belong in:

```text
tests/test_agent_service.py
tests/test_app_agent.py
```

Do not add broad natural-language parsing patterns without strong test coverage.

---

## Trusted Tool Results

After tool execution, the v1.0.0 agent returns trusted tool output directly.

It does not ask the model to rewrite the result.

This avoids:

- Reasoning leakage
- Prompt leakage
- Misrepresentation of tool output
- Unnecessary latency
- A second model failure
- False claims after successful execution

When changing result formatting, prefer deterministic formatters over a second unrestricted model call.

Tool output must accurately represent the completed operation.

---

## Agent Test Requirements

Agent changes should test:

- Direct-response decisions
- Tool-use decisions
- Invalid JSON
- Missing decision fields
- Unknown decision types
- Hallucinated tools
- Invalid tool arguments
- Low-risk automatic execution
- Medium-risk confirmation
- High-risk denial
- Confirmation approval
- Confirmation denial
- Pending-request blocking
- Conversation-context injection
- Persistent response history
- Deterministic routing
- Model bypass during deterministic routing
- Trusted result behavior
- Explicit command compatibility

Run agent tests:

```powershell
pytest tests\test_agent_models.py
pytest tests\test_agent_parser.py
pytest tests\test_agent_prompt.py
pytest tests\test_agent_service.py
pytest tests\test_app_agent.py
```

Run all related tests together:

```powershell
pytest tests\test_agent_models.py `
    tests\test_agent_parser.py `
    tests\test_agent_prompt.py `
    tests\test_agent_service.py `
    tests\test_app_agent.py
```

---

## Manual Agent Acceptance Testing

Automated tests do not fully validate real-model behavior.

Before an agent release, test with the configured Ollama model.

Recommended requests:

```text
What is the capital of Poland?
```

```text
What is 347 multiplied by 982?
```

```text
What files are in my workspace?
```

```text
Read agent-test.txt.
```

```text
Create a folder called Test Folder.
```

```text
confirm yes
```

```text
Create a file called hello.txt that says Hello World.
```

```text
confirm yes
```

```text
What time is it?
```

Confirm:

- No JSON is shown to the user.
- No `<think>` block is shown.
- No internal reasoning is shown.
- No prompt text is shown.
- Low-risk tools execute correctly.
- Medium-risk tools require confirmation.
- Denial prevents execution.
- Tool output matches actual state.
- Current time matches the computer.
- Explicit commands still work.

Remove previous test resources before rerunning creation tests:

```powershell
Remove-Item "workspace\Test Folder" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item "workspace\hello.txt" `
    -Force `
    -ErrorAction SilentlyContinue
```

---

## Adding a New Subsystem

A new subsystem may use this structure:

```text
src/atlas/subsystem/
├── __init__.py
├── exceptions.py
├── models.py
├── service.py
└── database.py
```

Not every subsystem needs every file.

The structure should reflect real responsibilities rather than forcing unnecessary layers.

Typical responsibilities:

- `exceptions.py` — subsystem-specific exceptions
- `models.py` — dataclasses and domain records
- `service.py` — validation and business logic
- `database.py` — persistence
- `__init__.py` — exported public interface

A new subsystem should include:

- Unit tests
- Integration tests where applicable
- Documentation
- Logging
- Typed interfaces
- Explicit error handling
- Security review

---

## Adding a New Model Provider

A provider must implement `ModelProvider`.

Example:

```python
class ExampleModelProvider(ModelProvider):
    """Provide responses through an example backend."""

    @property
    def provider_name(self) -> str:
        """Return the provider name."""
        return "Example"

    def generate_response(
        self,
        user_message: str,
    ) -> str:
        """Generate a normal model response."""
        ...
```

If native structured output is available:

```python
def generate_structured_response(
    self,
    user_message: str,
    schema: dict[str, Any],
) -> str:
    """Generate a schema-constrained response."""
    ...
```

Then:

1. Add the provider module.
2. Extend the provider factory.
3. Extend configuration if necessary.
4. Add unit tests.
5. Update `.env.example`.
6. Update `docs/configuration.md`.
7. Update `docs/agent.md`.
8. Update the changelog.

Provider implementations should normalize third-party errors into `ModelError`.

---

## Adding a New Tool

A tool must implement the `Tool` interface.

Every tool must provide:

- A unique name
- A clear model-readable description
- A parameter schema
- A risk classification
- Confirmation metadata
- Strict input validation
- A structured `ToolResult`

Example:

```python
class ExampleTool(Tool):
    """Perform an example operation."""

    @property
    def definition(self) -> ToolDefinition:
        """Return the tool definition."""
        return ToolDefinition(
            name="example",
            description="Perform an example operation.",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            risk_level=ToolRiskLevel.LOW,
            requires_confirmation=False,
        )

    def execute(
        self,
        arguments: dict[str, Any],
    ) -> ToolResult:
        """Execute the example operation."""
        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output="Example result.",
        )
```

Export it from:

```text
src/atlas/tools/builtin/__init__.py
```

Register it in application startup.

Because the agent tool catalog is dynamic, every registered tool becomes visible to the agent.

A tool description must therefore be clear enough for both:

- Developers
- Model tool selection

---

## Developing Filesystem Tools

Filesystem tools must never bypass `FileSystemService`.

Correct dependency chain:

```text
Filesystem Tool
        ↓
FileSystemService
        ↓
ScopedPathResolver
        ↓
Allowed Workspace
```

Every filesystem tool should:

- Receive `FileSystemService` through dependency injection.
- Validate domain-specific arguments.
- Never bypass `ScopedPathResolver`.
- Never access unrestricted filesystem paths.
- Never duplicate permission logic.
- Never weaken path validation.
- Enforce read or write limits.
- Convert filesystem validation failures into controlled tool errors.

Current filesystem tools include:

- `ListDirectoryTool`
- `FileInfoTool`
- `ReadTextFileTool`
- `CreateDirectoryTool`
- `WriteTextFileTool`

---

## Tool Security Checklist

Before registering a tool:

```text
[ ] Tool name is unique and stable
[ ] Description accurately explains behavior
[ ] Description supports correct model selection
[ ] Parameter schema is complete
[ ] Required fields are identified
[ ] Unknown parameters are rejected when appropriate
[ ] Input types are validated
[ ] Domain-specific values are validated
[ ] Resource limits are enforced
[ ] Risk level is accurate
[ ] Confirmation requirement is accurate
[ ] Sensitive arguments are excluded from logs
[ ] Tool cannot bypass the permission system
[ ] Tool cannot authorize itself
[ ] Normal behavior is tested
[ ] Invalid input is tested
[ ] Boundary behavior is tested
[ ] Permission behavior is tested
[ ] Agent-selected behavior is tested
[ ] Explicit-command behavior is tested
[ ] Documentation is updated
```

---

## Risk Classification

Use the lowest accurate risk classification.

### Low Risk

Use only when the tool:

- Does not materially modify user state
- Does not communicate externally
- Does not control hardware
- Does not expose sensitive information beyond an approved scope
- Is easy to reverse or has no persistent effect

Examples:

- Calculator
- Current time
- Directory listing
- Scoped text reading
- Scoped file metadata

### Medium Risk

Use when the tool:

- Modifies limited local state
- Creates or overwrites resources
- Opens applications
- Performs a limited external action
- Requires explicit user awareness

Examples:

- Directory creation
- Text-file writing
- Confirmation demonstration

Medium-risk tools require confirmation under the default policy.

### High Risk

Use when the tool:

- Deletes or irreversibly modifies data
- Executes unrestricted commands
- Sends messages or transactions
- Changes system configuration
- Makes purchases
- Controls access systems
- Controls physical hardware
- Could create safety consequences

High-risk tools are denied by the default v1.0.0 policy.

---

## Permission Tests

For low-risk tools, test that execution occurs immediately after validation.

For confirmation-controlled tools, test:

- The initial request does not execute.
- A pending request is created.
- The target state remains unchanged.
- Approval executes the saved request.
- Denial prevents execution.
- Invalid confirmation does not execute.
- A second request does not overwrite pending state.
- Pending state clears after approval.
- Pending state clears after denial.
- Sensitive arguments are not logged.

For high-risk tools, verify that the request never reaches the executor.

Run:

```powershell
pytest tests\test_permissions.py
pytest tests\test_tools.py
pytest tests\test_app.py
pytest tests\test_agent_service.py
pytest tests\test_app_agent.py
```

---

## Security Rules

Permission-related code must follow these rules:

- Validation must occur before authorization.
- Authorization must occur before execution.
- A tool must not authorize itself.
- Denied requests must never reach the executor.
- Confirmation-controlled requests must remain pending until approved.
- Unclear approval input must fail safely.
- Complete sensitive arguments must not be logged.
- High-risk actions must remain denied until stronger controls exist.
- Agent-selected requests must follow the same policy as explicit commands.
- Model output must never be treated as authorization.
- Prompt instructions must never replace enforcement in application code.

Filesystem-related code must follow these rules:

- Every path must pass through `ScopedPathResolver`.
- Outside-scope paths must be rejected.
- Parent traversal must be rejected after canonical resolution.
- Read and write limits must be enforced.
- Existing-file overwrite behavior must be explicit.
- State-changing operations must require confirmation.
- Tests must cover allowed and rejected paths.

Agent-related code must follow these rules:

- Parse and validate every structured decision.
- Reject unknown tool names.
- Reject invalid tool arguments.
- Never trust claims that an action already occurred.
- Never expose internal reasoning.
- Never expose prompts or hidden instructions.
- Preserve one-tool-per-request limits until the multi-step loop is implemented.
- Add deterministic enforcement for high-confidence safety-critical patterns when appropriate.

---

## Logging Rules

Log operational information such as:

- Request IDs
- Component names
- Provider names
- Tool names
- Risk levels
- Permission decisions
- Record IDs
- Durations
- Success or failure
- File paths when appropriate
- File sizes or character counts

Do not log:

- API keys
- Full user messages
- Complete prompts
- Memory contents
- Conversation contents
- File contents
- Passwords
- Private tokens
- Unnecessary personal data
- Complete sensitive tool arguments

Logs are for diagnostics and auditing, not user analytics.

---

## Never Commit

Never commit:

```text
.env
API keys
passwords
tokens
SQLite databases
workspace user files
private logs
generated secrets
local model artifacts
```

Before pushing, verify:

```powershell
git check-ignore .env
git check-ignore data\atlas_memory.db
git check-ignore logs\atlas.log
git check-ignore workspace\example.txt
```

If a secret is accidentally committed, deleting it from the current file is not sufficient.

The secret must be:

1. Revoked
2. Replaced
3. Removed from Git history where necessary

---

## Documentation Rules

Documentation must describe behavior that actually exists.

When implementation changes:

- Update the relevant subsystem document.
- Remove outdated claims.
- Update examples.
- Update diagrams.
- Update test counts when intentionally documented.
- Update current-version information.
- Record the release in `CHANGELOG.md`.
- Update `ROADMAP.md` when milestone status changes.
- Update `ARCHITECTURE.md` when subsystem relationships change.
- Update `docs/agent.md` when agent behavior changes.
- Update `docs/tools.md` when tool behavior changes.
- Update `docs/configuration.md` when settings change.
- Update `docs/development.md` when workflows change.

The changelog records completed work.

The roadmap records planned work.

Do not copy roadmap plans into the current-feature documentation as completed behavior.

---

## Continuous Integration

Project ATLAS uses GitHub Actions.

Workflow:

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

A pull request should not be merged while required checks are failing.

CI is a final verification layer, not a replacement for local testing.

---

## Complete Local Quality Check

Before committing, run:

```powershell
ruff check .
ruff format --check .
mypy src
pytest
git diff --check
```

Expected release-quality result:

```text
ruff check: passed
ruff format --check: passed
mypy: passed
pytest: all tests passed
git diff --check: no output
```

For v1.0.0, the expected test count is:

```text
204 passed
```

unless additional tests have intentionally been added.

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

Review staged changes:

```powershell
git status
git diff --staged
```

Check whitespace:

```powershell
git diff --check
```

Do not commit generated user files from `workspace/`.

---

## Commit Messages

Commit messages should be short and specific.

Examples:

```text
Add agent decision parser
Add deterministic file action routing
Fix Ollama reasoning output handling
Document ATLAS agent subsystem
Release ATLAS v1.0.0 agent foundation
```

Avoid vague messages:

```text
updates
changes
stuff
fixed code
final version
```

Create a commit:

```powershell
git commit -m "Add deterministic file action routing"
```

---

## Pushing to GitHub

Push a new branch and configure its upstream:

```powershell
git push -u origin feature/descriptive-feature-name
```

After upstream is configured:

```powershell
git push
```

Confirm the remote branch:

```powershell
git branch -vv
```

---

## Pull Requests

Pull requests should include:

- A clear title
- A summary of the implementation
- Security implications
- Tests added
- Manual testing performed
- Documentation updated
- Linked issues
- Closing keywords when appropriate

Example title:

```text
Release ATLAS v1.0.0 — Agent Foundation
```

Example testing section:

```markdown
## Testing

- Ruff passed
- Ruff formatting passed
- MyPy passed
- 204 pytest tests passed
- Ollama manual acceptance tests passed
```

Use closing keywords in the pull-request description when issues should close after merging:

```text
Closes #12
Closes #13
Closes #14
```

Issues close only when the pull request is merged into the repository's default branch.

---

## Merging a Completed Feature

Preferred GitHub workflow:

1. Push the feature branch.
2. Open a pull request into `master`.
3. Wait for CI.
4. Review the diff.
5. Squash and merge.
6. Pull the updated `master`.
7. Delete the completed branch.

After merging:

```powershell
git switch master
git pull origin master
```

Delete the local feature branch:

```powershell
git branch -d feature/descriptive-feature-name
```

Delete the remote branch when appropriate:

```powershell
git push origin --delete feature/descriptive-feature-name
```

---

## Version Releases

Every release should update:

- `pyproject.toml`
- `src/atlas/main.py`
- `tests/test_main.py`
- `CHANGELOG.md`
- `README.md`
- `ROADMAP.md`
- `ARCHITECTURE.md`
- Relevant subsystem documentation
- `docs/agent.md` when agent behavior changes
- `docs/tools.md` when tools change
- `docs/development.md` when workflow changes
- `docs/configuration.md` when settings change
- `.env.example` when configuration changes

Version numbers should match across:

```text
pyproject.toml
src/atlas/main.py
tests/test_main.py
README.md
CHANGELOG.md
ROADMAP.md
ARCHITECTURE.md
```

Historical changelog entries should retain their original version numbers.

---

## Release Checklist

```text
[ ] Feature scope is complete
[ ] Tests are added
[ ] Regression tests are added
[ ] Ruff linting passes
[ ] Ruff formatting passes
[ ] MyPy passes
[ ] Pytest passes
[ ] Manual acceptance testing passes
[ ] No internal reasoning leaks
[ ] No structured JSON leaks
[ ] Permission behavior is correct
[ ] Confirmation behavior is correct
[ ] Version numbers match
[ ] README.md updated
[ ] CHANGELOG.md updated
[ ] ROADMAP.md updated
[ ] ARCHITECTURE.md updated
[ ] docs/agent.md updated
[ ] docs/tools.md updated
[ ] docs/development.md updated
[ ] docs/configuration.md updated
[ ] Sensitive files remain ignored
[ ] Workspace user files remain ignored
[ ] Git diff reviewed
[ ] Release commit pushed
[ ] Pull request CI passes
[ ] Pull request merged
[ ] Git tag created
[ ] GitHub Release published
[ ] Milestone closed
```

---

## Tagging a Release

After merging into `master`:

```powershell
git switch master
git pull origin master
```

Create an annotated tag:

```powershell
git tag -a v1.0.0 `
    -m "Project ATLAS v1.0.0 — Agent Foundation"
```

Push the tag:

```powershell
git push origin v1.0.0
```

Confirm:

```powershell
git tag
```

Do not create the final release tag before the release commit is present on `master`.

---

## GitHub Release

Create the GitHub Release from the pushed tag.

Recommended title:

```text
Project ATLAS v1.0.0 — Agent Foundation
```

Release notes should summarize:

- Major capabilities
- Security behavior
- Important limitations
- Test status
- Upgrade information
- Known issues
- Next milestone

Use `CHANGELOG.md` as the source of truth.

---

## Definition of Done

A feature is complete only when:

1. The implementation works.
2. Tests cover new behavior.
3. Regression tests cover corrected bugs.
4. Static checks pass.
5. Errors are handled.
6. Security implications are considered.
7. Permissions are correct.
8. Logs are appropriate.
9. Documentation is updated.
10. The changelog is updated for a release.
11. Manual acceptance testing passes when real-model behavior is involved.
12. The feature is committed and pushed.
13. CI passes.
14. The pull request is reviewed and merged.

Final checklist:

```text
[ ] Implementation complete
[ ] Tests complete
[ ] Security reviewed
[ ] Tool risk metadata accurate
[ ] Permission behavior tested
[ ] Confirmation behavior tested
[ ] Denied operations cannot reach execution
[ ] Agent output validated
[ ] Sensitive data excluded from logs
[ ] Documentation current
[ ] Changelog current
[ ] CI passing
```