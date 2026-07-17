# Project Initialization Guide

**Last Updated**: 2026-07-17  
**Project**: Agents (LangChain Agent Framework with LangSmith Tracing)  
**Environment**: Docker-first development & production

---

## Overview

This guide documents the complete process to initialize a new LangChain agent project from scratch with Docker support and LangSmith tracing integration. The project is developed entirely within Docker containers—no local Python environment setup is required.

---

## Prerequisites

- **Docker Desktop** installed (includes docker-compose)
- **Text editor** or IDE (VS Code recommended)
- **LangSmith account** (free tier available at smith.langchain.com)
- **LangSmith API Key** (generated from LangSmith dashboard)

---

## Phase 1: Project Structure & Docker Foundation

### Step 1: Create Project Directory

```bash
mkdir agents
cd agents
```

### Step 2: Initialize Git Repository

```bash
git init
```

### Step 3: Create .gitignore

Create `.gitignore` file:

```
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

# Environment variables (secrets)
.env

# Generated outputs
outputs/
```

### Step 4: Create Python Version File

Create `.python-version`:

```
3.11.15
```

---

## Phase 2: Project Configuration

### Step 5: Create pyproject.toml

Define your project metadata and dependencies:

```toml
[project]
name = "agents"
version = "0.1.0"
description = "LangChain agent with LangSmith tracing"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "langsmith>=0.10.5",
]
```

### Step 6: Lock Dependencies

Run this locally (or in container):

```bash
uv lock
```

This creates `uv.lock` for reproducible builds.

---

## Phase 3: Docker Setup

### Step 7: Create Dockerfile

The Dockerfile uses Python 3.11-slim and uv for fast, reproducible builds:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "main.py"]
```

**Key points**:
- Uses `python:3.11-slim` for minimal image size
- Installs git (slim images don't include it) so the Dev Container gets full git support — Source Control panel, file colors, and `git` CLI inside the container
- `git config --system --add safe.directory /app` is baked into the image — without it, git refuses to work ("dubious ownership") because the container's root user operates on Windows-owned mounted files. System-level config survives rebuilds.
- Installs `uv` for fast dependency resolution
- Copies only config files first (Docker layer caching)
- Syncs dependencies with `uv sync --frozen` (reproducible)
- `ENV PATH` puts the venv's binaries first, so plain `python` uses the project environment (no `uv run` prefix needed)
- Copies application code last

### Step 7b: Create .dockerignore

Prevents local clutter (especially a leaked `.venv`) from entering the Docker build context:

```
.venv
__pycache__
.git
.gitignore
.env
.devcontainer
docs
Inputs
outputs
.vscode
*.pyc
.pytest_cache
```

**Why this matters**: On Windows, a `.venv` folder in the build context breaks the build with `invalid file request .venv/bin/python`.

### Step 8: Create docker-compose.dev.yml

Development Compose file with volume mounts for hot reload:

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: app-container
    working_dir: /app
    volumes:
      - .:/app
      - ./.env:/app/.env:ro
      - /app/.venv
    env_file:
      - .env
    command: sleep infinity
    tty: true
    stdin_open: true
```

**Key points**:
- `volumes: - .:/app` mounts local code into container (hot reload)
- `- ./.env:/app/.env:ro` mounts environment file read-only
- `- /app/.venv` (anonymous volume) keeps the venv **inside the container only** — without this, `.venv` leaks into your local folder through the bidirectional mount and breaks builds
- `env_file: - .env` loads variables into container
- `command: sleep infinity` keeps the container alive forever — **required for VS Code Dev Containers**. You run the app manually (`python main.py`) inside the container. If the command were `python main.py`, the container would exit as soon as the script finishes and VS Code could never attach.
- `tty: true` and `stdin_open: true` for interactive debugging

---

## Phase 4: LangSmith Integration

### Step 9: Create .env.example Template

For version control—shows required variables:

```
# LangSmith Configuration
LANGSMITH_API_KEY=your-api-key-here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=agents-dev

# Add other API keys here as needed
# DATABASE_URL=postgresql://user:pass@localhost/db
```

### Step 10: Create .env (Local, Not Committed)

Copy `.env.example` to `.env` and fill in real values:

```
LANGSMITH_API_KEY=lsv2_pt_<your-actual-key-here>
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=agents-dev
```

**Important**: `.env` is in `.gitignore` and never committed (contains secrets).

### Step 11: Create tracing.py

Centralizes LangSmith initialization and validation:

```python
import os
from langsmith import Client


def init_langsmith_tracing():
    """Initialize LangSmith tracing configuration."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    tracing_enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    project_name = os.getenv("LANGSMITH_PROJECT", "agents-dev")
    
    if not api_key:
        raise ValueError("LANGSMITH_API_KEY not set in .env file")
    
    if not tracing_enabled:
        print("⚠️  LangSmith tracing is disabled. Set LANGSMITH_TRACING=true in .env")
        return None
    
    client = Client(api_key=api_key)
    print(f"✅ LangSmith tracing initialized (Project: {project_name})")
    return client


def get_client():
    """Get the LangSmith client instance."""
    return init_langsmith_tracing()
```

### Step 12: Create main.py

Entry point with traced function:

```python
from tracing import get_client
from langsmith import traceable


@traceable(name="main_agent_workflow")
def agent_workflow():
    """Main agent workflow that will be traced to LangSmith."""
    print("🤖 Agent workflow started")
    
    result = "Agent completed successfully"
    print(f"✓ Result: {result}")
    return result


def main():
    print("Hello from agents!")
    
    client = get_client()
    if client:
        print("📊 Running with LangSmith tracing enabled")
        agent_workflow()
    else:
        print("⚠️  Running without tracing")


if __name__ == "__main__":
    main()
```

---

## Phase 5: Project Documentation & Structure

### Step 13: Create the Full Directory Scaffold

Create the complete package skeleton up front — empty files included — so development is purely "fill in the logic":

```bash
mkdir -p docs inputs outputs src/agent src/config src/models src/utils tests/fixtures

touch src/__init__.py \
      src/agent/__init__.py src/agent/core.py src/agent/tools.py \
      src/config/__init__.py src/config/settings.py \
      src/models/__init__.py src/models/schemas.py \
      src/utils/__init__.py src/utils/helpers.py \
      tests/__init__.py tests/test_agent.py tests/fixtures/.gitkeep
```

**What each part is for** (details in PROJECT_STRUCTURE.md):
- `src/agent/` — agent orchestration (core.py) and tool definitions (tools.py)
- `src/config/` — settings.py loads/validates environment config
- `src/models/` — schemas.py holds Pydantic models
- `src/utils/` — helpers.py for shared utilities
- `tests/` — test suite; `fixtures/.gitkeep` keeps the empty folder in git
- `outputs/` is git-ignored, so it exists locally but stays untracked

### Step 14: Create README.md

```markdown
# Agents Project

LangChain agent framework with LangSmith tracing.

## Quick Start

```bash
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

## Documentation

- **[COLLABORATION.md](docs/COLLABORATION.md)** — Developer workflow and roles
- **[PROGRESS.md](docs/PROGRESS.md)** — Project phase tracker
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** — Directory structure template
- **[COMMON_COMMANDS.md](docs/COMMON_COMMANDS.md)** — Development workflows & commands
```

### Step 15: Create COLLABORATION.md

Defines developer roles and workflow (see `docs/COLLABORATION.md`).

### Step 16: Create PROJECT_STRUCTURE.md

Documents the standardized folder layout for scalability (see `docs/PROJECT_STRUCTURE.md`).

### Step 17: Create PROGRESS.md

Tracks project phases and completion status (see `docs/PROGRESS.md`).

### Step 17b: Create .devcontainer/devcontainer.json (VS Code Dev Containers)

Lets VS Code run inside the container so Pylance sees the container's packages (no false import errors):

```json
{
  "name": "Agents Dev",
  "dockerComposeFile": "../docker-compose.dev.yml",
  "service": "app",
  "workspaceFolder": "/app",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.debugpy"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": false
      }
    }
  },
  "remoteUser": "root"
}
```

**Do NOT add a `postCreateCommand`** that installs packages — the Dockerfile already handles dependencies.

Full setup, daily workflow, and troubleshooting: see `docs/DOCKER_WORKFLOW.md`.

---

## Phase 6: Build & Verify

### Step 18: Build Docker Image

```bash
docker-compose -f docker-compose.dev.yml build
```

Expected output: `Image agents-app Built` with successful layer caching.

### Step 19: Start Container & Run the App

The dev container idles (`sleep infinity`), so start it detached and run the app manually:

```bash
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml exec app python main.py
```

(Or, if connected via Dev Containers, just run `python main.py` in the VS Code terminal.)

Expected output:
```
Hello from agents!
✅ LangSmith tracing initialized (Project: agents-dev)
📊 Running with LangSmith tracing enabled
🤖 Agent workflow started
✓ Result: Agent completed successfully
```

### Step 20: Verify LangSmith Dashboard

1. Go to https://smith.langchain.com/
2. Log in with your account
3. Find project "agents-dev"
4. Look for recent trace "main_agent_workflow"
5. Confirm trace shows input/output and execution time

---

## Final Directory Structure

After all steps, your project looks like:

```
agents/
├── .env                          # Local secrets (not committed)
├── .env.example                  # Template (committed)
├── .gitignore
├── .dockerignore
├── .python-version
├── pyproject.toml
├── uv.lock
├── README.md
├── Dockerfile
├── docker-compose.dev.yml
├── .devcontainer/
│   └── devcontainer.json
│
├── main.py                       # Entry point
├── tracing.py                    # LangSmith setup
│
├── docs/
│   ├── COLLABORATION.md
│   ├── PROJECT_STRUCTURE.md
│   ├── PROGRESS.md
│   └── COMMON_COMMANDS.md
│
├── src/                          # Agent packages (for Phase 2+)
│   ├── __init__.py
│   ├── agent/
│   ├── config/
│   └── utils/
│
└── inputs/                       # Test data
    └── (data files)
```

---

## Key Principles

1. **Docker-First Development** — No local Python setup; all work happens in containers
2. **Environment-Driven** — API keys and config via .env, never hardcoded
3. **Reproducible Builds** — uv.lock ensures identical dependencies every time
4. **Layered Caching** — Dockerfile structured for optimal Docker build caching
5. **Hot Reload** — Volume mounts let you edit code and see changes immediately
6. **Centralized Tracing** — LangSmith integration validates config and initializes cleanly

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `docker-compose: command not found` | Install Docker Desktop for your OS |
| `ModuleNotFoundError` for a package listed in pyproject.toml | `uv.lock` is stale — `uv sync --frozen` installs the lock, not pyproject. Run the canonical flow: `uv lock` (container) → `down`/`build`/`up -d` (host) → Reopen in Container (COMMON_COMMANDS.md Workflow 2) |
| `LANGSMITH_API_KEY not set` | Verify .env file exists in project root with your actual API key |
| Build fails: `invalid file request .venv/bin/python` | A local `.venv` leaked into the build context. Delete it, ensure `.venv` is in `.dockerignore`, and add `- /app/.venv` to compose volumes |
| Dev Container fails: "container ... is not running" | Compose `command` must be `sleep infinity` — a short-lived command exits before VS Code can attach |
| `.venv` keeps reappearing locally | Add anonymous volume `- /app/.venv` in docker-compose.dev.yml |
| `pip list` shows no packages in container | uv venvs have no bundled pip; use `uv pip list` or `python -c "import <pkg>"` |
| No traces in LangSmith | Wait 30 seconds and refresh; verify LANGSMITH_TRACING=true in .env |
| Permission denied on .env mount | Windows/Mac: usually works automatically; Linux: check file permissions |

---

## Next Steps

After Phase 1 is complete:
- **Phase 2**: Create src/ package structure and move application logic
- **Phase 3**: Define agent tools and integrations
- **Phase 4**: Add tests and CI/CD pipelines
