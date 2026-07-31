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

## Example Local Configuration

```dotenv
ATLAS_PROVIDER=ollama
ATLAS_MODEL=qwen3:4b
OLLAMA_HOST=http://localhost:11434

ATLAS_MEMORY_DATABASE=data/atlas_memory.db

ATLAS_LOG_DIRECTORY=logs
ATLAS_LOG_LEVEL=INFO
ATLAS_LOG_MAX_BYTES=5000000
ATLAS_LOG_BACKUP_COUNT=5

OPENAI_API_KEY=
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

---

## Logging Settings

### `ATLAS_LOG_DIRECTORY`

Directory containing runtime logs.

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

Maximum size of the active log file before rotation.

Default:

```dotenv
ATLAS_LOG_MAX_BYTES=5000000
```

This is approximately 5 MB.

### `ATLAS_LOG_BACKUP_COUNT`

Number of rotated log files retained.

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

Verify that the log is ignored:

```powershell
git check-ignore logs\atlas.log
```

---

## Configuration Loading

ATLAS loads `.env` when the application starts.

Changing a value generally requires:

1. Save `.env`.
2. Exit ATLAS.
3. Start ATLAS again.

You normally do not need to reinstall the package when changing providers or models.

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

### Ollama Connection Error

Check whether Ollama is running:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### Missing Model

Check installed models:

```powershell
ollama list
```

Download the configured model:

```powershell
ollama pull qwen3:4b
```

### Invalid Integer Setting

These settings must contain only integers:

```text
ATLAS_LOG_MAX_BYTES
ATLAS_LOG_BACKUP_COUNT
```

Correct:

```dotenv
ATLAS_LOG_BACKUP_COUNT=5
```

Incorrect:

```dotenv
ATLAS_LOG_BACKUP_COUNT=five
```

---

## Security Checklist

Before pushing code:

```powershell
git status
git check-ignore .env
git check-ignore data\atlas_memory.db
git check-ignore logs\atlas.log
```

The private `.env`, database, and runtime logs must not appear in the staged changes.