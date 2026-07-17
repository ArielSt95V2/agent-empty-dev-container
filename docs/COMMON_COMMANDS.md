# Common Commands & Development Workflows

Quick reference for commands and workflows you'll use during development.

---

## ⚡ The Golden Rule of This Setup

The dev container **idles forever** (`command: sleep infinity`) — the app does NOT auto-run.

- **Start environment** (host): `docker-compose -f docker-compose.dev.yml up -d`
- **Run the app** (inside container / VS Code Dev Container terminal): `python main.py`
- **Code changes**: hot reload via volume mount — just save and re-run, no rebuild
- **Dependency or Docker config changes**: rebuild (host): `down` → `build` → `up -d`

---

## Docker Compose Commands

### Build the Docker Image

Use this after updating dependencies in `pyproject.toml`:

```bash
docker-compose -f docker-compose.dev.yml build
```

**When to use**: After adding new packages to pyproject.toml

---

### Run the Container (Blocking)

Starts the container and attaches output. Stops when the script finishes:

```bash
docker-compose -f docker-compose.dev.yml up
```

**When to use**: Testing the full application run

---

### Run the Container (Background)

Starts the container in detached mode (runs in background):

```bash
docker-compose -f docker-compose.dev.yml up -d
```

**When to use**: Running the agent continuously while you work on other things

---

### Stop the Container

Stops a detached container:

```bash
docker-compose -f docker-compose.dev.yml down
```

**When to use**: After finishing development or before rebuilding

---

### View Container Logs

If running in detached mode, view logs:

```bash
docker-compose -f docker-compose.dev.yml logs -f
```

The `-f` flag means "follow" (stream logs in real-time). Remove it to see logs from the start.

**When to use**: Debugging issues or monitoring agent execution

---

### Execute Commands in Running Container

Run a command inside the container without stopping it:

```bash
docker-compose -f docker-compose.dev.yml exec app bash
```

This opens an interactive bash shell in the container.

**When to use**: Testing imports, running Python scripts interactively, debugging

---

### Rebuild and Run (Full Cycle)

Clean rebuild and run (useful after major changes):

```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up
```

**When to use**: After changing Dockerfile or dependencies

---

## Typical Development Workflows

### Workflow 1: Iterative Development

```bash
# 1. Start the container in background
docker-compose -f docker-compose.dev.yml up -d

# 2. Make code changes in main.py, tracing.py, etc.
# (Hot reload: changes visible immediately)

# 3. View updated logs
docker-compose -f docker-compose.dev.yml logs -f

# 4. When done, stop
docker-compose -f docker-compose.dev.yml down
```

---

### Workflow 2: Adding a New Dependency

```bash
# 1. Edit pyproject.toml and add dependency under [project] dependencies

# 2. Rebuild Docker image (picks up new dependencies)
docker-compose -f docker-compose.dev.yml build

# 3. Run to test
docker-compose -f docker-compose.dev.yml up

# Verify the new package is installed and works
```

---

### Workflow 3: Debugging in Container

```bash
# 1. Start container in background
docker-compose -f docker-compose.dev.yml up -d

# 2. Open interactive shell
docker-compose -f docker-compose.dev.yml exec app bash

# 3. Inside the container, run Python interactively
python3

# 4. Test imports, check variables, etc.
# >>> from tracing import get_client
# >>> print(get_client())

# 5. Exit Python and container
# >>> exit()
# root@container# exit
```

---

### Workflow 4: After a Long Break

If you haven't run the project in a while and want a clean start:

```bash
docker-compose -f docker-compose.dev.yml down       # Stop & remove container
docker-compose -f docker-compose.dev.yml build      # Rebuild image (fresh deps)
docker-compose -f docker-compose.dev.yml up         # Run
```

---

## Environment & Configuration Commands

### Check Environment Variables in Container

```bash
docker-compose -f docker-compose.dev.yml exec app env
```

Verify your .env variables are loaded (look for LANGSMITH_API_KEY, LANGSMITH_TRACING).

---

### Reload Environment After Editing .env

Stop and restart the container:

```bash
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up
```

Docker reloads .env on each start.

---

## Shortcuts & Aliases (Optional)

Add these to your shell profile (`.bashrc`, `.zshrc`, or PowerShell profile) for faster development:

### Bash / Zsh

```bash
# ~/.bashrc or ~/.zshrc
alias dev-build="docker-compose -f docker-compose.dev.yml build"
alias dev-up="docker-compose -f docker-compose.dev.yml up"
alias dev-down="docker-compose -f docker-compose.dev.yml down"
alias dev-logs="docker-compose -f docker-compose.dev.yml logs -f"
alias dev-shell="docker-compose -f docker-compose.dev.yml exec app bash"
```

Then use:
```bash
dev-up          # Instead of docker-compose -f docker-compose.dev.yml up
dev-logs        # Instead of docker-compose -f docker-compose.dev.yml logs -f
dev-shell       # Drop into container bash
```

### PowerShell

Add to your PowerShell profile (`$PROFILE`):

```powershell
function dev-build { docker-compose -f docker-compose.dev.yml build }
function dev-up { docker-compose -f docker-compose.dev.yml up }
function dev-down { docker-compose -f docker-compose.dev.yml down }
function dev-logs { docker-compose -f docker-compose.dev.yml logs -f }
function dev-shell { docker-compose -f docker-compose.dev.yml exec app bash }
```

Then use:
```powershell
dev-up
dev-logs
dev-shell
```

---

## Git Commands (During Development)

Git is installed **inside the dev container** (via the Dockerfile), and the container shares the same repository as your local folder. Run these from the VS Code Dev Container terminal (recommended — keeps everything in one window) or from the host; both operate on the exact same repo state.

### Check Status

```bash
git status
```

Before committing, verify what files are staged.

---

### Stage Changes

```bash
git add .
```

Add all modified files to staging area. (Exclude .env automatically via .gitignore)

---

### Commit Changes

```bash
git commit -m "Add agent tool for weather API"
```

Keep commit messages clear and concise.

---

### View Recent Commits

```bash
git log --oneline -10
```

See last 10 commits in compact format.

---

## Useful Docker Commands

### Remove Unused Images

Over time, Docker accumulates old images. Clean them up:

```bash
docker image prune -a
```

Removes all unused images (asks for confirmation).

---

### View Running Containers

```bash
docker ps
```

Shows active containers. Add `-a` to see all (including stopped).

---

### View All Images

```bash
docker images
```

See all Docker images on your system.

---

## Quick Reference Cheat Sheet

| Task | Command |
|------|---------|
| Build image | `docker-compose -f docker-compose.dev.yml build` |
| Run once | `docker-compose -f docker-compose.dev.yml up` |
| Run in background | `docker-compose -f docker-compose.dev.yml up -d` |
| Stop container | `docker-compose -f docker-compose.dev.yml down` |
| View logs | `docker-compose -f docker-compose.dev.yml logs -f` |
| Shell in container | `docker-compose -f docker-compose.dev.yml exec app bash` |
| Full rebuild cycle | `down && build && up` |
| Check env vars | `docker-compose -f docker-compose.dev.yml exec app env` |
| See running containers | `docker ps` |
| Clean up old images | `docker image prune -a` |

---

## Troubleshooting Commands

### Container Won't Start

```bash
# Check logs for errors
docker-compose -f docker-compose.dev.yml logs

# Full output (verbose)
docker-compose -f docker-compose.dev.yml logs --tail=50
```

---

### Import Errors in Container

```bash
# Drop into container shell
docker-compose -f docker-compose.dev.yml exec app bash

# Check if package is installed
pip list | grep langsmith

# Try importing manually
python3 -c "from langsmith import Client; print('OK')"
```

---

### Clear Docker Cache (Nuclear Option)

If something is broken and you want to start completely fresh:

```bash
docker-compose -f docker-compose.dev.yml down
docker system prune -a --volumes
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up
```

⚠️ This removes ALL Docker data. Use only as a last resort.

---

## Summary

**Daily development** usually looks like:

```bash
# Morning (host): Start the environment
docker-compose -f docker-compose.dev.yml up -d
# Then in VS Code: "Reopen in Container" (if not already connected)

# Throughout the day (VS Code terminal, inside container):
python main.py          # run the app whenever you want to test
# Edit code freely — hot reload means no rebuilds

# End of day (host): Stop
docker-compose -f docker-compose.dev.yml down
```

For most workflows, you'll only use 3 commands:
1. `build` — After changing dependencies
2. `up` / `up -d` — Run the app
3. `down` — Stop and clean up
