# Installing Project ATLAS

This guide explains how to install and run Project ATLAS for local development.

ATLAS is currently developed and tested primarily on Windows using Python, PowerShell, VS Code, and Ollama.

---

## Current Requirements

Before installing ATLAS, install:

- Python 3.13 or newer
- Git
- Visual Studio Code
- Ollama, when using a local AI model

Recommended VS Code extensions:

- Python by Microsoft
- Pylance by Microsoft
- Ruff by Astral Software

---

## Verify the Required Software

Open PowerShell and run:

```powershell
python --version
git --version
```

When using Ollama, also run:

```powershell
ollama --version
```

Each command should return a version number.

On some Windows systems, Python may be available through the `py` launcher instead:

```powershell
py --version
```

---

## Clone the Repository

Clone Project ATLAS from GitHub:

```powershell
git clone https://github.com/victoriajarocki/Project-ATLAS.git
```

Replace `victoriajarocki` with the GitHub username that owns the repository.

Enter the project directory:

```powershell
cd Project-ATLAS
```

---

## Create a Virtual Environment

Create a project-specific Python environment:

```powershell
python -m venv .venv
```

If the `python` command is unavailable, use:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

The terminal prompt should begin with:

```text
(.venv)
```

For example:

```text
(.venv) PS C:\Users\YourName\Documents\Project-ATLAS>
```

### PowerShell Script Policy

If PowerShell reports that scripts are disabled, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirm the change when prompted, then activate the environment again:

```powershell
.venv\Scripts\Activate.ps1
```

---

## Select the Python Interpreter in VS Code

In VS Code:

1. Press `Ctrl + Shift + P`.
2. Search for `Python: Select Interpreter`.
3. Select the interpreter located in `.venv`.

The selected interpreter should resemble:

```text
Project-ATLAS\.venv\Scripts\python.exe
```

Verify from the terminal:

```powershell
python -c "import sys; print(sys.executable)"
```

The output should contain:

```text
Project-ATLAS\.venv
```

---

## Install ATLAS

Upgrade `pip`:

```powershell
python -m pip install --upgrade pip
```

Install ATLAS and its development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

The `-e` option installs ATLAS in editable mode. Source-code changes become available without reinstalling the package after every edit.

---

## Configure Environment Variables

Create a private `.env` file from the example configuration:

```powershell
Copy-Item .env.example .env
```

A typical local Ollama configuration is:

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

The `.env` file is private and must never be committed to Git.

Confirm that Git ignores it:

```powershell
git check-ignore .env
```

Expected output:

```text
.env
```

See [Configuration](configuration.md) for a complete explanation of the available settings.

---

## Configure Ollama

Install Ollama and verify that it is available:

```powershell
ollama --version
```

Download the recommended development model:

```powershell
ollama pull qwen3:4b
```

Verify that the model exists:

```powershell
ollama list
```

Test it directly:

```powershell
ollama run qwen3:4b
```

Exit the Ollama conversation with:

```text
/bye
```

ATLAS communicates with Ollama through:

```text
http://localhost:11434
```

---

## Run ATLAS

Start ATLAS:

```powershell
atlas
```

The startup screen should display the installed version and enabled subsystems.

For example:

```text
ATLAS v0.7.0
Model provider: Ollama
Persistent memory: Enabled
Conversation sessions: Enabled
Tool system: Enabled
```

Exit ATLAS with:

```text
exit
```

---

## Run the Development Checks

Run linting:

```powershell
ruff check .
```

Verify formatting:

```powershell
ruff format --check .
```

Run static type checking:

```powershell
mypy src
```

Run the unit tests:

```powershell
pytest
```

Run all checks before committing changes:

```powershell
ruff check .
ruff format --check .
mypy src
pytest
```

---

## Local Files

ATLAS creates local runtime files that are intentionally excluded from Git:

```text
.env
.venv/
data/atlas_memory.db
logs/atlas.log
```

These contain local configuration, installed packages, user memory, conversations, or runtime logs.

---

## Common Problems

### `atlas` Is Not Recognized

Make sure the virtual environment is active:

```powershell
.venv\Scripts\Activate.ps1
```

Reinstall the project:

```powershell
python -m pip install -e ".[dev]"
```

Open a new PowerShell terminal and retry:

```powershell
atlas
```

### Ollama Cannot Be Reached

Make sure Ollama is running, then test its local API:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

### Model Is Missing

Download the model named in `ATLAS_MODEL`:

```powershell
ollama pull qwen3:4b
```

### Tests Cannot Import ATLAS

Confirm that the virtual environment is active and reinstall the editable package:

```powershell
python -m pip install -e ".[dev]"
```

---

## Next Steps

After installation:

1. Read [Development](development.md).
2. Review [Configuration](configuration.md).
3. Explore the [Tool System](tools.md).
4. Review the project-level `ARCHITECTURE.md`.
5. Review the project-level `ROADMAP.md`.