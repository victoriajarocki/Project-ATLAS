# Project ATLAS Configuration

ATLAS uses environment variables for runtime configuration.

Private configuration belongs in:

```text
.env
```

A safe template belongs in:

```text
.env.example
```

The real `.env` file must never be committed to Git.

---

## Creating the Configuration File

From the project root:

```powershell
Copy-Item .env.example .env
```

Confirm that Git ignores it:

```powershell
git check-ignore .env
```

Expected output:

```text
.env
```

---

## Complete Local Configuration Example

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

Version 1.0.0 does not introduce additional agent-specific environment variables.

The agent uses:

- The configured model provider
- The configured model
- Registered tool definitions
- Existing permission policies
- Existing filesystem boundaries
- Existing memory and conversation services

---

# Model Provider Settings

## `ATLAS_PROVIDER`

Selects the active model provider.

Supported values:

```text
mock
openai
ollama
```

Example:

```dotenv
ATLAS_PROVIDER=ollama
```

---

## Mock Provider

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
```

The Mock provider:

- Requires no API key
- Requires no network connection
- Produces deterministic responses
- Is useful for testing application infrastructure
- Is used by automated tests through scripted providers and test fixtures

The Mock provider is not intended to provide real natural-language reasoning.

---

## Ollama Provider

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434
```

The Ollama provider enables local model inference.

The selected model must already be installed:

```powershell
ollama list
```

Install the recommended local development model when necessary:

```powershell
ollama pull qwen3:4b
```

Confirm that Ollama is reachable:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Version 1.0.0 uses Ollama for:

- Natural-language responses
- Structured agent decisions
- JSON-schema-constrained output
- Automatic tool selection

The Ollama provider automatically configures structured agent requests with:

- JSON-schema output
- Thinking disabled
- Low-temperature generation
- Output-length limits
- Model keep-alive behavior
- Defensive output cleanup

These settings are currently implemented by the provider and are not configurable through `.env`.

---

## OpenAI Provider

```dotenv
ATLAS_PROVIDER=openai
ATLAS_MODEL=YOUR_SUPPORTED_MODEL
OPENAI_API_KEY=YOUR_PRIVATE_KEY
```

API billing is separate from a ChatGPT subscription.

Never place a real API key in:

```text
.env.example
README.md
source files
tests
GitHub Issues
pull-request descriptions
commit messages
```

The OpenAI provider must use a model supported by the installed provider implementation.

---

## `ATLAS_MODEL`

Specifies the model selected for the active provider.

Examples:

```dotenv
ATLAS_MODEL=mock-model
```

```dotenv
ATLAS_MODEL=qwen3:4b
```

The name must be valid for the active provider.

Agent quality may vary between models.

A model used for the v1.0.0 agent should reliably support:

- Instruction following
- Structured JSON generation
- Tool selection
- Basic conversation context
- Short final responses

The current recommended local development model is:

```text
qwen3:4b
```

---

## `OLLAMA_HOST`

Specifies the Ollama API address.

Default:

```dotenv
OLLAMA_HOST=http://localhost:11434
```

Most local installations should keep this value unchanged.

A custom host may be used when Ollama runs on another approved machine:

```dotenv
OLLAMA_HOST=http://192.168.1.25:11434
```

Remote Ollama access may expose user prompts and context to another device.

Use a remote host only when the device and network are trusted.

---

## `OPENAI_API_KEY`

Stores the private API key used by the OpenAI provider.

Example:

```dotenv
OPENAI_API_KEY=YOUR_PRIVATE_KEY
```

The key is required only when:

```dotenv
ATLAS_PROVIDER=openai
```

The value must remain in the private `.env` file.

Do not place a real key in `.env.example`.

---

# Agent Configuration

Version 1.0.0 introduces the ATLAS agent foundation.

The current agent does not require separate environment variables.

When the agent is enabled during application construction, it automatically uses:

- The active model provider
- The registered tool catalog
- The shared tool validator
- The active permission policy
- Conversation context
- Persistent-memory context
- Configured filesystem boundaries

Current agent behavior includes:

- Direct-response decisions
- Single-tool decisions
- Natural-language tool selection
- Structured decision parsing
- Permission-aware execution
- Confirmation-controlled state changes
- Deterministic routing for recognized file and folder creation requests
- Trusted tool-result responses

The current agent is limited to one model-selected tool per request.

Future releases may add configuration such as:

```text
ATLAS_AGENT_MAX_STEPS
ATLAS_AGENT_TIMEOUT_SECONDS
ATLAS_AGENT_RETRY_LIMIT
ATLAS_AGENT_PLANNING_MODE
```

These variables are not currently implemented and must not be added to `.env` until corresponding source-code support exists.

---

# Persistence Settings

## `ATLAS_MEMORY_DATABASE`

Specifies the SQLite file used for persistent memory and conversation history.

Default:

```dotenv
ATLAS_MEMORY_DATABASE=data/atlas_memory.db
```

The database contains local user data and must remain excluded from Git.

Verify:

```powershell
git check-ignore data\atlas_memory.db
```

ATLAS currently uses the same SQLite database path for:

- Persistent memories
- Conversation metadata
- Conversation messages

Agent-generated responses and trusted tool results may be stored in conversation history.

Future releases may separate these storage locations.

---

# Logging Settings

## `ATLAS_LOG_DIRECTORY`

Specifies the directory containing runtime logs.

Default:

```dotenv
ATLAS_LOG_DIRECTORY=logs
```

The directory is created when necessary.

---

## `ATLAS_LOG_LEVEL`

Controls the minimum logging severity.

Supported levels:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Default:

```dotenv
ATLAS_LOG_LEVEL=INFO
```

Use `DEBUG` only when investigating a problem:

```dotenv
ATLAS_LOG_LEVEL=DEBUG
```

Version 1.0.0 logs agent operations such as:

- Structured decision requests
- Direct-response selection
- Tool selection
- Deterministic routing
- Permission decisions
- Confirmation resolution
- Tool execution
- Request duration

ATLAS logs message lengths and operation metadata rather than complete private content.

---

## `ATLAS_LOG_MAX_BYTES`

Specifies the maximum size of the active log file before rotation.

Default:

```dotenv
ATLAS_LOG_MAX_BYTES=5000000
```

This is approximately 5 MB.

The value must be a positive integer.

---

## `ATLAS_LOG_BACKUP_COUNT`

Specifies the number of rotated log files retained.

Default:

```dotenv
ATLAS_LOG_BACKUP_COUNT=5
```

Example rotated logs:

```text
atlas.log
atlas.log.1
atlas.log.2
```

The value must be zero or greater.

Verify that the active log is ignored:

```powershell
git check-ignore logs\atlas.log
```

---

# Filesystem Settings

ATLAS uses secure local filesystem access introduced in v0.9.0 and integrated with the agent in v1.0.0.

Filesystem operations are restricted to explicitly configured directories.

The agent cannot bypass these boundaries.

---

## `ATLAS_ALLOWED_DIRECTORIES`

Specifies the directories that ATLAS may access.

Default:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Relative paths are resolved from the directory where ATLAS is started.

For consistent behavior, launch ATLAS from the project root:

```powershell
cd C:\Users\vixky\Documents\Project-ATLAS
atlas
```

An absolute path may also be used:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=C:\Users\vixky\Documents\Project-ATLAS\workspace
```

Multiple allowed directories may be separated with semicolons:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace;C:\Users\vixky\Documents\ATLAS-Documents
```

ATLAS requires at least one non-empty directory value.

If a configured directory does not exist, the scoped path resolver creates it during startup.

A configured allowed path must represent a directory rather than a file.

---

## Relative Path Behavior

Relative tool paths resolve against the first configured allowed directory.

For example:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

An explicit request such as:

```text
tool read_text_file {"path": "Rocket Design/notes.txt"}
```

and a natural-language request such as:

```text
Read Rocket Design/notes.txt.
```

resolve to:

```text
<Project-ATLAS>/workspace/Rocket Design/notes.txt
```

When the user asks:

```text
What files are in my workspace?
```

the agent normally selects `list_directory` with:

```json
{
  "path": "."
}
```

The relative path `.` represents the first configured allowed directory.

---

## Windows JSON Paths

Use forward slashes inside explicit JSON tool commands:

```text
Rocket Design/notes.txt
```

Forward slashes work on Windows and avoid JSON escape-sequence problems.

A single backslash can be interpreted as an escape sequence:

```text
Rocket Design\notes.txt
```

For example, `\n` becomes a newline.

Escaped backslashes also work:

```text
Rocket Design\\notes.txt
```

Forward slashes are recommended.

Natural-language requests do not require JSON escaping, but the agent-generated tool arguments still pass through the same scoped path resolver.

---

## `ATLAS_FILESYSTEM_MAX_READ_BYTES`

Specifies the maximum file size ATLAS may read through `read_text_file`.

Default:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
```

The default permits files up to approximately 1 MB.

The value must be a positive integer.

A file larger than this limit is rejected before its contents are read.

Example smaller limit:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=100000
```

This limit applies equally to:

- Explicit tool commands
- Agent-selected tool requests

---

## `ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS`

Specifies the maximum number of characters ATLAS may write through `write_text_file`.

Default:

```dotenv
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

The value must be a positive integer.

Content exceeding this limit is rejected before the file is modified.

Example smaller limit:

```dotenv
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=100000
```

This limit applies equally to:

- Explicit tool commands
- Agent-selected tool requests
- Deterministically routed file-creation requests

---

# Filesystem Security Behavior

The filesystem configuration establishes the root boundaries used by `ScopedPathResolver`.

Requests outside those boundaries are rejected.

Examples of rejected paths include:

```text
../README.md
../../Windows/System32
C:/Windows/System32
```

An absolute path is accepted only when it remains inside a configured allowed directory.

Current filesystem protections include:

- Canonical path resolution
- Parent-traversal rejection
- Absolute-path scope validation
- UTF-8-only text reading
- Configurable read limits
- Configurable write limits
- Existing-file overwrite protection
- Confirmation for state-changing tools
- Shared behavior for explicit and agent-selected tools

The following tools use filesystem configuration:

```text
list_directory
file_info
read_text_file
create_directory
write_text_file
```

For the complete subsystem design, see:

```text
docs/filesystem.md
```

---

# Workspace Configuration

The default local workspace is:

```text
workspace/
```

The folder is retained in Git using:

```text
workspace/.gitkeep
```

Workspace contents should remain excluded through `.gitignore`:

```gitignore
workspace/*
!workspace/.gitkeep
```

Confirm that a sample workspace file is ignored:

```powershell
git check-ignore workspace\example.txt
```

Expected output:

```text
workspace\example.txt
```

The `.gitkeep` file itself should remain tracked.

Agent-created files and directories inside `workspace/` are local runtime data and should not be committed.

---

# Configuration Loading

ATLAS loads `.env` when the application starts.

Changing a value generally requires:

1. Save `.env`.
2. Exit ATLAS.
3. Start ATLAS again.

You normally do not need to reinstall the package when changing:

- Providers
- Models
- Ollama host
- Log levels
- Filesystem limits
- Allowed directories

Reinstall the editable package only when project dependencies or package metadata change:

```powershell
python -m pip install -e ".[dev]"
```

Restarting ATLAS is important because:

- The provider is created during startup.
- The agent receives that provider during startup.
- Filesystem roots are resolved during startup.
- Logging is configured during startup.

---

# Inspecting Loaded Configuration

You can inspect selected values through Python.

## Active Provider

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().provider)"
```

## Active Model

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().model)"
```

## Ollama Host

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().ollama_host)"
```

## Allowed Directories

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().allowed_directories)"
```

## Filesystem Limits

```powershell
python -c "from atlas.config.settings import load_settings; s=load_settings(); print(s.filesystem_max_read_bytes); print(s.filesystem_max_write_characters)"
```

## Resolved Filesystem Path

```powershell
python -c "from atlas.config.settings import load_settings; from atlas.filesystem.paths import ScopedPathResolver; s=load_settings(); r=ScopedPathResolver(s.allowed_directories); p=r.resolve('Rocket Design/notes.txt'); print('Allowed roots:', r.allowed_directories); print('Resolved file:', p); print('Exists:', p.exists())"
```

This is useful when diagnosing workspace-path problems.

---

# Switching Between Providers

## Switch to Mock

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
```

## Switch to Ollama

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434
```

## Switch to OpenAI

```dotenv
ATLAS_PROVIDER=openai
ATLAS_MODEL=YOUR_SUPPORTED_MODEL
OPENAI_API_KEY=YOUR_PRIVATE_KEY
```

Restart ATLAS:

```powershell
atlas
```

The startup display should report:

- The selected provider
- Memory status
- Conversation status
- Tool status
- Permission status
- Agent status

---

# Recommended Development Configuration

## Local Agent Development with Ollama

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

Use this configuration for:

- Real natural-language responses
- Real structured agent decisions
- Manual tool-selection testing
- Manual confirmation testing
- Local-first operation

---

## Offline Infrastructure Configuration

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
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

Use this configuration for infrastructure development that does not require real model behavior.

Automated tests should use isolated settings and scripted providers rather than relying on the developer's `.env`.

---

# Troubleshooting

## ATLAS Still Uses the Old Provider

Confirm the `.env` file is located in the project root:

```powershell
Get-ChildItem -Force
```

Check the value Python loads:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('ATLAS_PROVIDER'))"
```

Restart ATLAS after saving `.env`.

---

## Ollama Connection Error

Check whether Ollama is running:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Verify the configured host:

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().ollama_host)"
```

Confirm that the Ollama application is running before launching ATLAS.

---

## Missing Ollama Model

Check installed models:

```powershell
ollama list
```

Download the configured model:

```powershell
ollama pull qwen3:4b
```

Confirm that the `.env` model name exactly matches the installed model name.

---

## Agent Returns Invalid JSON

The v1.0.0 agent requests a structured decision from the active provider.

When using Ollama, verify:

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
```

Confirm that the configured model supports structured responses reliably.

Restart Ollama and ATLAS when necessary.

Review recent logs:

```powershell
Get-Content logs\atlas.log -Tail 100
```

The visible error may resemble:

```text
The model response was not valid JSON.
```

Do not weaken the parser to accept arbitrary model output.

Structured decisions must remain validated.

---

## Agent Displays Internal Reasoning

The Ollama provider is designed to:

- Disable thinking
- Request final output only
- Remove leaked `<think>` blocks
- Limit generated output

Confirm that the current provider implementation is installed:

```powershell
python -m pip install -e ".[dev]"
```

Restart ATLAS.

Review:

```text
src/atlas/models/ollama_provider.py
```

The application should never intentionally display:

```text
<think>
```

internal analysis, prompt instructions, or planning text.

---

## Agent Claims an Action Happened Without Confirmation

Recognized file and folder creation requests should be routed deterministically.

Examples:

```text
Create a folder called Test Folder.
```

```text
Create a file called hello.txt that says Hello World.
```

Expected behavior:

```text
Tool create_directory requires confirmation.
```

or:

```text
Tool write_text_file requires confirmation.
```

If the model instead claims completion:

1. Confirm that the latest `AgentService` is installed.
2. Restart ATLAS.
3. Run:

```powershell
python -m pip install -e ".[dev]"
```

4. Run the deterministic-routing tests:

```powershell
pytest tests\test_agent_service.py
pytest tests\test_app_agent.py
```

5. Confirm the request matches a supported deterministic pattern.

---

## Tool Request Remains Pending

While a medium-risk request is pending, ATLAS accepts:

```text
confirm yes
```

or:

```text
confirm no
```

Unrelated requests are blocked until the pending request is resolved.

If the request should not execute, use:

```text
confirm no
```

Pending requests exist only in memory and are cleared when the ATLAS process exits.

---

## File or Directory Already Exists

The current filesystem tools reject existing targets unless overwrite behavior is explicitly enabled and supported.

Check:

```powershell
Test-Path "workspace\Test Folder"
Test-Path "workspace\hello.txt"
```

Remove disposable test resources:

```powershell
Remove-Item "workspace\Test Folder" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item "workspace\hello.txt" `
    -Force `
    -ErrorAction SilentlyContinue
```

Then restart the test.

Do not remove real user data without verifying the path first.

---

## Current Time Is Incorrect

The `current_time` tool uses:

```python
datetime.now().astimezone()
```

It therefore uses the timezone configured by the operating system.

Check Windows settings:

```text
Settings
→ Time & language
→ Date & time
→ Time zone
```

The tool should return a readable result such as:

```text
Current local time

Saturday, August 01, 2026
8:10:48 PM EDT
```

If the offset is correct but the displayed zone abbreviation is unexpected, verify the system timezone and daylight-saving settings.

---

## Filesystem File Does Not Exist

First verify the real file:

```powershell
Test-Path -LiteralPath "workspace\Rocket Design\notes.txt"
```

List workspace contents:

```powershell
Get-ChildItem workspace -Force -Recurse |
    Select-Object FullName, PSIsContainer
```

Check the resolved ATLAS path:

```powershell
python -c "from atlas.config.settings import load_settings; from atlas.filesystem.paths import ScopedPathResolver; s=load_settings(); r=ScopedPathResolver(s.allowed_directories); p=r.resolve('Rocket Design/notes.txt'); print(p); print(p.exists())"
```

If the resolved path is not inside the intended project workspace, verify:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Make sure ATLAS was started from the project root.

You may instead configure an absolute directory path.

---

## Path Appears on Multiple Lines

This usually means a single Windows backslash was used inside explicit JSON:

```text
Rocket Design\notes.txt
```

The sequence `\n` becomes a newline.

Use:

```text
Rocket Design/notes.txt
```

or:

```text
Rocket Design\\notes.txt
```

---

## Path Outside Allowed Scope

An error stating that a path is outside configured directories means the path resolved beyond an allowed root.

Review:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Ensure the requested file is physically located inside that directory.

Do not weaken the scope check merely to make an outside path work.

Add another intentional allowed root instead:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace;C:\Users\vixky\Documents\Approved-ATLAS-Files
```

---

## File Exceeds Read Limit

Increase:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
```

only when the larger limit is intentional.

The current tool supports UTF-8 text files only.

---

## Content Exceeds Write Limit

Increase:

```dotenv
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

only when the larger write is expected.

---

## Invalid Integer Setting

These settings must contain integer values:

```text
ATLAS_LOG_MAX_BYTES
ATLAS_LOG_BACKUP_COUNT
ATLAS_FILESYSTEM_MAX_READ_BYTES
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS
```

Correct:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
```

Incorrect:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=one-million
```

---

## Empty Allowed Directories

This is invalid:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=
```

ATLAS requires at least one allowed directory.

Use:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

---

# Configuration Validation

ATLAS validates configuration during startup.

Examples of invalid configuration include:

- Empty model name
- Empty Ollama host
- Empty database path
- Empty log directory
- Non-integer numeric settings
- Negative or zero filesystem limits
- Empty allowed-directory configuration

Startup stops safely when required configuration is invalid.

Agent startup depends on valid:

- Provider configuration
- Tool registration
- Permission-service construction
- Filesystem-service construction

The current agent does not add separate startup settings.

---

# Security Checklist

Before pushing code:

```powershell
git status
git check-ignore .env
git check-ignore data\atlas_memory.db
git check-ignore logs\atlas.log
git check-ignore workspace\example.txt
```

The following must not appear in staged changes:

- Private `.env`
- API keys
- SQLite databases
- Runtime logs
- User workspace files
- Private document contents
- Model prompt transcripts
- Complete agent conversation history

Review staged changes:

```powershell
git diff --staged
```

Search for accidental secrets:

```powershell
git grep -n "OPENAI_API_KEY="
```

The safe `.env.example` file should contain empty or placeholder secrets only.

---

# Configuration Reference

| Variable | Default | Purpose |
|---|---|---|
| `ATLAS_PROVIDER` | `mock` | Select the model provider |
| `ATLAS_MODEL` | `mock-model` | Select the provider model |
| `OPENAI_API_KEY` | Empty | Authenticate the OpenAI provider |
| `OLLAMA_HOST` | `http://localhost:11434` | Configure the Ollama API |
| `ATLAS_MEMORY_DATABASE` | `data/atlas_memory.db` | Store memory and conversations |
| `ATLAS_LOG_DIRECTORY` | `logs` | Store runtime logs |
| `ATLAS_LOG_LEVEL` | `INFO` | Set minimum log severity |
| `ATLAS_LOG_MAX_BYTES` | `5000000` | Set log-rotation size |
| `ATLAS_LOG_BACKUP_COUNT` | `5` | Retain rotated logs |
| `ATLAS_ALLOWED_DIRECTORIES` | `workspace` | Define filesystem access roots |
| `ATLAS_FILESYSTEM_MAX_READ_BYTES` | `1000000` | Limit text-file reads |
| `ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS` | `1000000` | Limit text-file writes |

There are currently no separate agent-specific environment variables.

---

# Summary

ATLAS configuration is designed to be:

- Environment-driven
- Local-first
- Strongly validated
- Testable
- Secure by default
- Easy to change without modifying source code
- Shared consistently by explicit commands and agent-selected actions

Version 1.0.0 builds the agent foundation on top of the existing provider, persistence, logging, permission, tool, and filesystem configuration.

The agent does not weaken or replace existing security settings. Every model-selected action remains subject to the same validation, permission, confirmation, and scoped-resource boundaries as an explicit command.