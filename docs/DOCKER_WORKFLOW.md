# Docker Workflow & VS Code Dev Containers

Complete guide to Docker-first development with hot reload and integrated debugging.

---

## Overview

This project uses **Docker containers for all development and production**. You never run Python locally—everything happens inside Docker. **Volume mounts** sync your code changes instantly to the container without rebuilds.

---

## Part 1: Understanding Volume Mounts (Hot Reload)

### What Are Volume Mounts?

Volume mounts are bridges between your local machine and the Docker container:

```yaml
volumes:
  - .:/app                    # Your local code → container's /app
  - ./.env:/app/.env:ro       # Your .env → container's .env (read-only)
  - /app/.venv                # Anonymous volume: .venv stays in container ONLY (never syncs to Windows)
```

**Critical**: The `/app/.venv` line (no local path before the colon) makes Docker use an anonymous volume for that folder. Without it, the container's `.venv` leaks into your local project folder through the bidirectional mount — which breaks Docker builds on Windows.

### The Key Insight: Two Types of Changes

| Change Type | Example | Action Needed |
|---|---|---|
| **Python code** | Edit `main.py` | ✅ None—container sees change instantly (hot reload) |
| **Dependencies** | Edit `pyproject.toml` | ❌ Must rebuild: `docker-compose build && docker-compose up` |
| **Docker config** | Edit `Dockerfile` or `docker-compose.yml` | ❌ Must rebuild: `docker-compose build && docker-compose up` |

### How Hot Reload Works

```
1. You edit main.py locally in VS Code
                ↓
2. Docker volume mount syncs change to /app/main.py in container
                ↓
3. Container sees updated file immediately
                ↓
4. Re-run or check logs—new code executes
                ↓
5. No container restart needed! ⚡
```

---

## Part 2: Host Terminal vs. Container Terminal

### Host Terminal (Your Computer)

These commands run **on your local machine**:

```bash
# Docker orchestration (start/stop/rebuild)
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
docker-compose -f docker-compose.dev.yml down

# View logs from container (but run from host)
docker-compose -f docker-compose.dev.yml logs -f

# Git version control (also works INSIDE the container — see Part 6)
git add .
git commit -m "Update agent"
git push

# Edit files in VS Code
# (Changes appear in container via volume mount)
```

### Container Terminal (Inside Docker)

These commands run **inside the container** (access via `docker-compose exec app bash`):

```bash
# Python operations
python3 main.py
python3 -c "from tracing import get_client; print(get_client())"

# Package inspection (already installed from pyproject.toml)
pip list
pip show langsmith

# Debugging
python3 -i  # Interactive Python

# File operations inside container
ls -la /app
cat /app/main.py
```

### Quick Reference Table

| Task | Where? | Command |
|------|--------|---------|
| Build Docker image | Host terminal | `docker-compose build` |
| Start container | Host terminal | `docker-compose up` |
| Stop container | Host terminal | `docker-compose down` |
| View logs | Host terminal | `docker-compose logs -f` |
| Edit Python files | VS Code (host) | Edit locally, changes sync automatically |
| Test imports in Python | Container terminal | `python3 -c "from X import Y"` |
| Check installed packages | Container terminal | `pip list` |
| Git operations | Either — container recommended for one-window workflow | `git add/commit/push` |

---

## Part 3: VS Code Dev Containers Setup

### Why Use Dev Containers?

Dev Containers run VS Code **inside the Docker container**, giving you:
- ✅ Pylance checks container's Python (no false import errors)
- ✅ Terminal in VS Code is already inside container (no `docker-compose exec` needed)
- ✅ All extensions run inside container
- ✅ Debugger works inside container
- ✅ Hot reload still works via volume mounts

### Step 1: Install Dev Containers Extension

1. Open VS Code
2. Go to Extensions (`Ctrl+Shift+X`)
3. Search for "Dev Containers"
4. Install (by Microsoft)

### Step 2: Create `.devcontainer/devcontainer.json`

**File location**: `C:\Users\astab\Desktop\Coding\agents\.devcontainer\devcontainer.json`

**Action**: Create this file with content (copy-paste exactly):

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

**Note**: Do NOT add a `postCreateCommand` that installs packages — the Dockerfile's `uv sync` already handles dependencies, and a duplicate install step can create a stray `.venv` and crash the container setup.

**Also required**: the dev compose file must keep the container alive. In `docker-compose.dev.yml`:

```yaml
command: sleep infinity
```

A dev container must run forever so VS Code can live inside it. If the command is `python main.py`, the script finishes in a second, the container exits, and VS Code fails with "container is not running". You run the app manually instead (see Part 4).

**What this does**:
- `dockerComposeFile` — Points to your `docker-compose.dev.yml`
- `service: app` — Runs VS Code in the `app` service container
- `extensions` — Installs Python, Pylance, and debugger inside container
- `python.defaultInterpreterPath` — Sets container's Python as interpreter
- `remoteUser: root` — Runs container as root user

### Step 3: Reopen in Container

**Action**:
1. Open command palette in VS Code (`Ctrl+Shift+P`)
2. Type "Dev Containers: Reopen in Container"
3. Wait 30-60 seconds for container to build and extensions to install
4. VS Code reloads and you're now inside the container ✅

**First time only**: It will build the container, install dependencies, and install extensions. This takes 1-2 minutes.

### Step 4: Verify It Works

**In VS Code terminal (now inside container)**:

```bash
# Should show container's Python
which python3
# Output: /usr/local/bin/python3

# Test Pylance by opening main.py
# No more "Import langsmith could not be resolved" errors! ✅
```

---

## Part 4: Daily Development Workflow

### Morning: Start Fresh

```bash
# In Host terminal
docker-compose -f docker-compose.dev.yml down

# Open folder in VS Code
# VS Code asks: "Folder contains Dev Container config, reopen in container?"
# Click "Reopen in Container"

# Wait for setup (30 seconds)
```

### All Day: Edit & Hot Reload

```
Edit main.py in VS Code
    ↓
Volume mount syncs change instantly
    ↓
Run it in the VS Code terminal (inside container):
    python main.py
    ↓
See output immediately — new code, no rebuild
```

**No rebuilds. No restarts. Just edit and run.** ⚡

**Remember**: The dev container idles (`sleep infinity`) — the app does NOT auto-run. You run `python main.py` on demand whenever you want to test.

### When Adding Dependencies

```bash
# In VS Code terminal (inside container)
# Edit pyproject.toml to add new package

# In Host terminal (exit VS Code terminal)
docker-compose -f docker-compose.dev.yml down

# Back in Host terminal
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up

# VS Code reconnects automatically
```

### End of Day: Stop

```bash
# In Host terminal
docker-compose -f docker-compose.dev.yml down
```

---

## Part 5: Local vs. Container - Which Files Go Where?

### Critical Rule

**If container won't start**: Edit config files **locally**, then rebuild.

### Files You Edit Locally (Config Files)

These affect container setup. Edit locally, then rebuild container:

```
.devcontainer/devcontainer.json    ← Dev Containers config
Dockerfile                          ← Docker image setup
docker-compose.dev.yml              ← Container orchestration
pyproject.toml                      ← Dependencies
.gitignore                          ← Git rules
.env                                ← Secrets (local only, never in container)
```

**After editing these**: 
```bash
# Host terminal
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
# VS Code: Ctrl+Shift+P → "Dev Containers: Reopen in Container"
```

### Files You Edit in Container (Application Code)

Edit these inside VS Code (Dev Container). Volume mount syncs to local automatically:

```
main.py                     ← Entry point
tracing.py                  ← Tracing config
src/agent/core.py           ← Agent logic
src/config/settings.py      ← App settings
src/utils/helpers.py        ← Utilities
```

**After editing these**: No rebuild needed. Changes appear instantly.

### Quick Decision Tree

```
Question: Which file do I need to edit?

├─ Is it a config file? (.devcontainer, Dockerfile, .env, pyproject.toml)
│  └─ YES: Edit locally → rebuild container
│
└─ Is it application code? (main.py, src/*, etc.)
   └─ YES: Edit in VS Code (Dev Container) → instant hot reload
```

---

## Part 6: Git in the Dev Container (Single-Window Workflow)

### Why

With git installed inside the container, the **one** Dev Container window gives you everything: Source Control panel, file colors in the Explorer (green = new, yellow = modified), gutter change indicators, and diff views. No second local window needed.

### How It Works

- The `.git` folder lives in `/app` via the volume mount — container and local folder share the **same repository**. A commit made in the container is instantly the local repo's state too. There is no second copy and no syncing.
- **The Dockerfile installs git** (slim Python images don't include it) and bakes in the ownership fix:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && git config --system --add safe.directory /app
```

- **Why `safe.directory /app` at system level**: the container runs as root over Windows-owned files, so git refuses to operate ("detected dubious ownership") without it. Setting it with `--system` bakes it into the image — a `--global` setting made inside a running container would be lost on every rebuild.
- **Credentials & identity are automatic**: VS Code forwards your host git credentials (HTTPS credential helper / SSH agent) and copies your host `.gitconfig` (user.name / user.email) into the container. `git push` from the container just works — no separate login.

### Verify After a Rebuild

```bash
git --version                                  # Linux git (e.g. 2.47.x), not "windows"
git config --system --get-all safe.directory   # → /app
git status                                     # works, no ownership warning
git config user.name ; git config user.email   # identity copied from host
```

### What Stays on the Host

Docker orchestration only: `docker-compose build/up/down` — the container can't run Docker itself. Git, editing, and running the app all happen in the container window.

---

## Part 7: Troubleshooting Dev Containers

### Issue: "Setting up container" fails with "container ... is not running"

**Cause**: The compose `command` runs a short-lived script (e.g. `python main.py`), so the container exits right after starting — before VS Code can attach.

**Solution**: In `docker-compose.dev.yml`, set `command: sleep infinity`. Rebuild-free fix: `docker-compose down`, then Reopen in Container. Run the app manually inside with `python main.py`.

### Issue: A `.venv` folder keeps appearing in the local project

**Cause**: The Dockerfile's `uv sync` creates `/app/.venv` in the container, and the bidirectional `.:/app` mount syncs it back to Windows. It then poisons the next Docker build (`invalid file request .venv/bin/python`).

**Solution**: Three layers of defense:
1. Add `- /app/.venv` (anonymous volume) to the compose `volumes:` list — stops the sync.
2. Add `.venv` to `.dockerignore` — stops it from entering the build context.
3. If one already leaked locally: delete it (`Remove-Item .venv -Recurse -Force`), then rebuild.

### Issue: `pip list` inside the container shows nothing

**Cause**: uv-created virtualenvs do not bundle their own `pip`, so `pip` resolves to the system pip, which lists system packages — not the project's.

**Solution**: Use `uv pip list`, or verify a specific package with `python -c "import langsmith; print(langsmith.__version__)"`. If `python main.py` runs, dependencies are fine.

### Issue: "Reopen in Container" fails with `.venv/bin/python`

**Cause**: Local `.venv` doesn't exist (Docker-first)

**Solution**: 
1. Delete `.devcontainer/devcontainer.json`
2. Recreate it using the exact content from Step 2 above
3. Ensure `python.defaultInterpreterPath` points to `/usr/local/bin/python` (container path)

### Issue: Pylance still shows import errors

**Cause**: Pylance is still checking local Python

**Solution**:
1. Verify you're "inside" container: Check VS Code bottom-left for "Dev Container" badge
2. In VS Code terminal, run: `which python3` → should show `/usr/local/bin/python3`
3. Reload window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Issue: Terminal in VS Code is still on host, not container

**Cause**: Dev Containers didn't attach properly

**Solution**:
1. Close all VS Code terminals
2. Close VS Code entirely
3. Run: `docker-compose -f docker-compose.dev.yml down`
4. Reopen folder in VS Code
5. Wait for full reconnection (watch bottom-left badge)

### Issue: Changes don't appear in container after editing

**Cause**: Volume mount not synced or container crashed

**Solution**:
```bash
# In Host terminal
docker-compose -f docker-compose.dev.yml logs -f

# Look for errors. If none, restart:
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

# Then in VS Code: Ctrl+Shift+P → "Dev Containers: Reopen in Container"
```

---

## Summary: The Three-Layer Model

```
┌─────────────────────────────┐
│   VS Code GUI (your screen) │  ← You interact here
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  Dev Containers Extension   │  ← Bridges host ↔ container
│  (runs inside container)    │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│  Docker Container           │  ← Python runs here
│  - Python 3.11              │  ← All packages installed
│  - langsmith, etc.          │  ← Pylance checks here
│  - /app (volume mount)      │  ← Your code synced here
└─────────────────────────────┘
```

**Key principle**: You edit locally, Python runs in container, volume mounts keep them in sync.

---

## Glossary

- **Volume mount**: Shared folder between host and container (`.:/app`)
- **Hot reload**: Changes visible immediately without restart
- **Dev Containers**: VS Code inside Docker (not on host)
- **docker-compose build**: Builds the Docker image from Dockerfile
- **docker-compose up**: Starts the container from the image
- **remoteUser**: Which user to run in container (root = full access)
