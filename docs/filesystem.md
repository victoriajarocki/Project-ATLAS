# Secure Filesystem

The ATLAS filesystem subsystem provides controlled access to local files while enforcing strict security boundaries.

Rather than allowing unrestricted access to the host operating system, all filesystem operations are confined to explicitly configured workspace directories.

The subsystem is designed around the principles of:

- Least privilege
- Explicit authorization
- Defense in depth
- Path safety
- Local-first execution
- Modular architecture

---

# Purpose

The filesystem subsystem allows ATLAS to safely interact with local files without exposing unrestricted operating system access.

Current capabilities include:

- Directory listing
- File metadata inspection
- Reading UTF-8 text files
- Writing UTF-8 text files
- Directory creation

All operations are routed through a centralized service layer.

---

# Architecture

Filesystem requests follow the pipeline below.

```text
User
   │
   ▼
ATLAS Core
   │
   ▼
Tool Registry
   │
   ▼
Shared Argument Validation
   │
   ▼
Permission Service
   │
   ▼
Permission Policy
   │
   ▼
Tool Executor
   │
   ▼
Filesystem Tool
   │
   ▼
FileSystemService
   │
   ▼
ScopedPathResolver
   │
   ▼
Allowed Workspace
```

Each layer performs a specific responsibility.

---

# Components

## ScopedPathResolver

Responsible for safely resolving user-supplied paths.

Responsibilities include:

- Path normalization
- Relative path resolution
- Absolute path validation
- Canonical path generation
- Scope enforcement

Every filesystem operation passes through the resolver.

---

## FileSystemService

The service layer responsible for filesystem operations.

Current operations include:

- list_directory()
- get_info()
- read_text_file()
- create_directory()
- write_text_file()

The service performs:

- existence checks
- file/directory validation
- UTF-8 decoding
- size validation
- overwrite protection

The service never performs permission decisions.

---

## Built-in Filesystem Tools

Current filesystem tools:

| Tool | Risk | Confirmation |
|-------|------|--------------|
| list_directory | Low | No |
| file_info | Low | No |
| read_text_file | Low | No |
| create_directory | Medium | Yes |
| write_text_file | Medium | Yes |

The permission subsystem determines whether execution is allowed.

Filesystem tools never authorize themselves.

---

# Workspace Sandboxing

ATLAS only operates inside configured directories.

Default configuration:

```dotenv
ATLAS_ALLOWED_DIRECTORIES=workspace
```

Workspace structure:

```text
workspace/
    Rocket Design/
    Projects/
    Notes/
```

Operations outside configured roots are rejected.

---

# Path Resolution

User paths may be supplied as:

```text
notes.txt
```

or

```text
Projects/notes.txt
```

The resolver converts these into canonical absolute paths before validation.

---

# Path Traversal Protection

Attempts such as

```text
../secret.txt
```

or

```text
../../Windows/System32
```

are rejected.

The resolver validates the fully resolved canonical path before execution.

This prevents escaping the configured workspace.

---

# File Reading

Current implementation supports:

- UTF-8 text
- configurable maximum file size

Configuration:

```dotenv
ATLAS_FILESYSTEM_MAX_READ_BYTES=1000000
```

Binary files are intentionally unsupported.

---

# File Writing

Writing supports:

- UTF-8 text
- configurable maximum size
- overwrite validation

Configuration:

```dotenv
ATLAS_FILESYSTEM_MAX_WRITE_CHARACTERS=1000000
```

Medium-risk writes require explicit confirmation.

---

# Directory Creation

Directory creation is considered a state-changing operation.

Execution requires:

1. validation
2. permission approval
3. user confirmation
4. filesystem execution

---

# Permission Integration

Filesystem tools integrate directly with the permission subsystem.

Current behavior:

| Operation | Decision |
|-----------|----------|
| List directory | Allow |
| Read file | Allow |
| File information | Allow |
| Create directory | Confirm |
| Write file | Confirm |

High-risk filesystem operations are currently unsupported.

---

# Shared Validation

Filesystem tools use the centralized JSON schema validator.

Validation occurs before permission evaluation.

Example schema:

```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string"
    }
  },
  "required": [
    "path"
  ]
}
```

Domain-specific validation remains inside the filesystem subsystem.

---

# Logging

Filesystem activity is logged through the observability subsystem.

Typical events include:

- directory listing
- file reads
- file writes
- permission decisions
- execution timing

Log files intentionally exclude:

- complete file contents
- credentials
- secrets

---

# Error Handling

Filesystem exceptions include:

- FileSystemError
- FileSystemValidationError
- PathOutsideAllowedScopeError
- FileSystemOperationError

Errors are converted into user-friendly tool responses by the tool framework.

---

# Security Model

Filesystem protection relies on multiple independent layers.

```text
Command Parsing
        │
        ▼
JSON Validation
        │
        ▼
Permission Evaluation
        │
        ▼
Scoped Path Resolution
        │
        ▼
Filesystem Operation
        │
        ▼
Audit Logging
```

Each layer protects against a different category of failure.

---

# Current Limitations

Version 0.9 intentionally limits filesystem functionality.

Unsupported features include:

- file deletion
- file renaming
- file copying
- binary file support
- symbolic links
- recursive search
- wildcard expansion

These capabilities will be considered in future releases after additional security review.

---

# Future Development

Planned enhancements include:

- File deletion
- File renaming
- Copy and move operations
- Binary file support
- Recursive directory search
- File search
- PDF support
- Image support
- Document indexing
- Semantic search
- Workspace management

Future versions will continue expanding filesystem functionality while preserving the security-first architecture established in v0.9.0.

---

# Summary

The filesystem subsystem provides Project ATLAS with secure, local-first access to user files.

Current implementation emphasizes:

- scoped access
- explicit authorization
- defense in depth
- modular design
- centralized validation
- comprehensive logging

The subsystem forms the foundation for future capabilities including document understanding, semantic search, engineering workflows, and autonomous task execution.