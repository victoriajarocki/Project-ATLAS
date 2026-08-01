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

---

## Model Provider Settings

### `ATLAS_PROVIDER`

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

### Mock Provider

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
```

The Mock provider:

- Requires no API key
- Requires no network connection
- Produces deterministic responses
- Is useful for testing infrastructure

### Ollama Provider

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434
```

The selected model must already be installed:

```powershell
ollama list
```

Install it when necessary:

```powershell
ollama pull qwen3:4b
```

### OpenAI Provider

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
commit messages
```

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

---

## `OLLAMA_HOST`

Specifies the Ollama API address.

Default:

```dotenv
OLLAMA_HOST=http://localhost:11434
```

Most local installations should keep this value unchanged.

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

## Persistence Settings

### `ATLAS_MEMORY_DATABASE`

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

Future releases may separate these storage locations.

---

## Logging Settings

### `ATLAS_LOG_DIRECTORY`

Specifies the directory containing runtime logs.

Default:

```dotenv
ATLAS_LOG_DIRECTORY=logs
```

### `ATLAS_LOG_LEVEL`

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

### `ATLAS_LOG_MAX_BYTES`

Specifies the maximum size of the active log file before rotation.

Default:

```dotenv
ATLAS_LOG_MAX_BYTES=5000000
```

This is approximately 5 MB.

The value must be a positive integer.

### `ATLAS_LOG_BACKUP_COUNT`

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

## Filesystem Settings

ATLAS v0.9.0 introduces secure local filesystem access.

Filesystem operations are restricted to explicitly configured directories.

### `ATLAS_ALLOWED_DIRECTORIES`

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

### Relative Path Behavior

Relative tool paths resolve against the first configured allowed directory.

For example:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

and:

```text
tool read_text_file {"path": "Rocket Design/notes.txt"}
```

resolve to:

```text
<Project-ATLAS>/workspace/Rocket Design/notes.txt
```

### Windows JSON Paths

Use forward slashes inside JSON tool commands:

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

---

### `ATLAS_FILESYSTEM_MAX_READ_BYTES`

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

---

### `ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS`

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

---

## Filesystem Security Behavior

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

## Workspace Configuration

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

---

## Configuration Loading

ATLAS loads `.env` when the application starts.

Changing a value generally requires:

1. Save `.env`.
2. Exit ATLAS.
3. Start ATLAS again.

You normally do not need to reinstall the package when changing:

- Providers
- Models
- Log levels
- Filesystem limits
- Allowed directories

Reinstall the editable package only when project dependencies or package metadata change:

```powershell
python -m pip install -e ".[dev]"
```

---

## Inspecting Loaded Configuration

You can inspect selected values through Python.

### Active Provider

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().provider)"
```

### Active Model

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().model)"
```

### Allowed Directories

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().allowed_directories)"
```

### Filesystem Limits

```powershell
python -c "from atlas.config.settings import load_settings; s=load_settings(); print(s.filesystem_max_read_bytes); print(s.filesystem_max_write_characters)"
```

### Resolved Filesystem Path

```powershell
python -c "from atlas.config.settings import load_settings; from atlas.filesystem.paths import ScopedPathResolver; s=load_settings(); r=ScopedPathResolver(s.allowed_directories); p=r.resolve('Rocket Design/notes.txt'); print('Allowed roots:', r.allowed_directories); print('Resolved file:', p); print('Exists:', p.exists())"
```

This is useful when diagnosing workspace-path problems.

---

## Switching Between Providers

### Switch to Mock

```dotenv
ATLAS_PROVIDER=mock
ATLAS_MODEL=mock-model
```

### Switch to Ollama

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434
```

### Switch to OpenAI

```dotenv
ATLAS_PROVIDER=openai
ATLAS_MODEL=YOUR_SUPPORTED_MODEL
OPENAI_API_KEY=YOUR_PRIVATE_KEY
```

Restart ATLAS:

```powershell
atlas
```

The startup display should report the selected provider.

---

## Recommended Development Configuration

A local Ollama configuration:

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

A fully offline testing configuration:

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

---

## Troubleshooting

### ATLAS Still Uses the Old Provider

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

### Ollama Connection Error

Check whether Ollama is running:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

Verify the configured host:

```powershell
python -c "from atlas.config.settings import load_settings; print(load_settings().ollama_host)"
```

---

### Missing Ollama Model

Check installed models:

```powershell
ollama list
```

Download the configured model:

```powershell
ollama pull qwen3:4b
```

---

### Filesystem File Does Not Exist

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

and make sure ATLAS was started from the project root.

You may instead configure an absolute directory path.

---

### Path Appears on Multiple Lines

This usually means a single Windows backslash was used inside JSON:

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

### Path Outside Allowed Scope

An error stating that a path is outside configured directories means the path resolved beyond an allowed root.

Review:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Then ensure the requested file is physically located inside that directory.

Do not weaken the scope check merely to make an outside path work.

Add another intentional allowed root instead:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace;C:\Users\vixky\Documents\Approved-ATLAS-Files
```

---

### File Exceeds Read Limit

Increase:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
```

only when the larger limit is intentional.

The current tool supports UTF-8 text files only.

---

### Content Exceeds Write Limit

Increase:

```dotenv
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

only when the larger write is expected.

---

### Invalid Integer Setting

These settings must contain only integers:

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

### Empty Allowed Directories

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

## Configuration Validation

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

---

## Security Checklist

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

## Configuration Reference

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

---

## Summary

ATLAS configuration is designed to be:

- Environment-driven
- Local-first
- Strongly validated
- Testable
- Secure by default
- Easy to change without modifying source code

The v0.9.0 filesystem settings extend this design by making local file access explicit, scoped, and configurable.