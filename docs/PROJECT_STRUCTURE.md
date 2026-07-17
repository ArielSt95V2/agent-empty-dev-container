# Project Structure Template

This document defines the standardized folder and file layout for LangChain Agent projects. Use this as a template for all future agent projects.

---

## Directory Tree

```
agents/
├── .env                          # Environment variables (API keys, secrets) - NOT committed
├── .env.example                  # Template .env (committed) - shows required vars
├── .gitignore                    # Git ignore patterns
├── .python-version               # Python version specifier (3.11+)
│
├── pyproject.toml                # Project metadata & dependencies
├── uv.lock                       # Locked dependency versions (for reproducible builds)
├── README.md                     # Project overview
├── COLLABORATION.md              # Developer workflow & roles
├── PROGRESS.md                   # Phase tracker
├── PROJECT_STRUCTURE.md          # This file - structural template
│
├── Dockerfile                    # Production container image
├── docker-compose.dev.yml        # Development environment (Docker)
├── docker-compose.yml            # Production environment (Docker)
│
├── main.py                       # Entry point / orchestrator
├── tracing.py                    # LangSmith tracing setup
│
├── src/                          # Source code packages
│   ├── __init__.py
│   ├── agent/                    # Agent logic & orchestration
│   │   ├── __init__.py
│   │   ├── core.py               # Main agent class
│   │   └── tools.py              # Tool definitions
│   ├── config/                   # Configuration & settings
│   │   ├── __init__.py
│   │   └── settings.py           # Environment config loader
│   ├── models/                   # Data models & schemas
│   │   ├── __init__.py
│   │   └── schemas.py            # Pydantic models
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_agent.py
│   └── fixtures/                 # Test data & mocks
│
├── inputs/                       # Input data files for testing
│   └── Full Day - Simulation.txt
│
└── outputs/                      # Generated outputs (not committed)
    └── (auto-generated results)
```

---

## File Purposes

### Root Configuration Files

| File | Purpose |
|------|---------|
| `.env` | **Not committed**. Contains: LANGSMITH_API_KEY, LANGSMITH_TRACING, API_KEY_* for any services |
| `.env.example` | **Committed**. Template showing required variables with placeholder values |
| `pyproject.toml` | Project name, version, Python version, dependencies, scripts |
| `uv.lock` | Frozen dependency versions for reproducible Docker builds |
| `Dockerfile` | Container image for production deployments |
| `docker-compose.dev.yml` | Local development environment (mounts source, .env, enables hot reload) |
| `docker-compose.yml` | Production-ready orchestration (no mounts, uses built image) |

### Documentation

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick-start instructions |
| `COLLABORATION.md` | Developer roles, workflow, communication style |
| `PROGRESS.md` | Phase tracker—what's done, what's next |
| `PROJECT_STRUCTURE.md` | This file—structural template for consistency |

### Python Source Code (`src/`)

| Module | Purpose |
|--------|---------|
| `agent/core.py` | Main agent class, orchestration logic |
| `agent/tools.py` | Tool definitions, integrations with external APIs |
| `config/settings.py` | Load environment variables, validate config |
| `models/schemas.py` | Pydantic models for type safety |
| `utils/helpers.py` | Shared utility functions (logging, formatting, etc.) |

### Entry Points

| File | Purpose |
|------|---------|
| `main.py` | Orchestrator—loads config, initializes tracing, runs agent |
| `tracing.py` | LangSmith client initialization & validation |

### Test & Data

| Folder | Purpose |
|--------|---------|
| `tests/` | Unit and integration tests |
| `inputs/` | Input data files (training data, simulation data, etc.) |
| `outputs/` | Generated results (git-ignored) |

---

## Key Principles

1. **src/ package structure** — All agent code goes in `src/` for clean imports
2. **Docker-first** — Code runs in containers in dev and prod
3. **Environment-driven** — No hardcoded values; use .env and config modules
4. **Modular organization** — Separate concerns (agent, config, utils, models)
5. **Clear entry point** — `main.py` is the only script; it orchestrates everything else

---

## Initialization Checklist for New Agent Projects

- [ ] Create `pyproject.toml` with Python 3.11+, dependencies
- [ ] Create `Dockerfile` (python:3.11-slim, uv-based)
- [ ] Create `docker-compose.dev.yml` with volume mounts and .env binding
- [ ] Create `main.py` and `tracing.py` entry points
- [ ] Create `src/` package structure with agent/, config/, utils/, models/
- [ ] Create `.env.example` with template variables
- [ ] Create `COLLABORATION.md`, `PROGRESS.md`, `PROJECT_STRUCTURE.md`
- [ ] Set `.gitignore` to exclude .env, __pycache__, .venv, outputs/

---

## Notes

- `.env` is **intentionally not committed** (it contains secrets)
- `.env.example` shows the template so collaborators know what to configure
- `outputs/` folder is git-ignored; any generated results go there
- Docker volumes for dev ensure code changes are hot-reloaded in the container
