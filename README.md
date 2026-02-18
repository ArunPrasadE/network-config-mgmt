# Network Configuration Backup System

Multi-vendor network configuration backup and change tracking system.
Collects running configs from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate devices,
detects changes, and generates diff reports. Includes a web UI (React + FastAPI) and CLI.

---

## Prerequisites

The **only** host-level requirement is a running Docker Engine with `docker compose`.
No Python, Node.js, or Ansible needed on your machine — everything runs inside a single container.

| Platform | Docker Runtime |
|----------|---------------|
| macOS (personal) | Docker Desktop, [Colima](https://github.com/abiosoft/colima), [OrbStack](https://orbstack.dev/), or [Rancher Desktop](https://rancherdesktop.io/) |
| macOS (company — no Docker Desktop license) | Colima (free, open-source): `brew install colima docker && colima start` |
| Windows | [Docker Desktop](https://www.docker.com/products/docker-desktop/) with WSL2 integration |
| Linux | [Docker Engine](https://docs.docker.com/engine/install/) |

Verify Docker Compose is available:
```bash
docker compose version
```

---

## First-Time Setup

### 1. Clone the repo

```bash
git clone git@github.com:ArunPrasadE/network-config-mgmt.git
cd network-config-mgmt
git checkout docker-compose
```

### 2. Authenticate with GitHub Container Registry (one-time)

The Docker image is hosted on **ghcr.io** (GitHub's container registry — not Docker Hub).
Both machines need to authenticate once:

1. Create a GitHub Personal Access Token at https://github.com/settings/tokens
   - Token type: **Classic**
   - Scopes needed: `read:packages` (Mac), or `write:packages` (WSL2 — if you push images)

2. Login to ghcr.io:
```bash
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u ArunPrasadE --password-stdin
```

### 3. Create credentials file

`playbooks/group_vars/all.yml` is **not committed** (contains passwords). Create it from the template:

```bash
cp .env.example playbooks/group_vars/all.yml
```

Edit `playbooks/group_vars/all.yml` with your device credentials:

```yaml
ansible_user: admin
ansible_password: "your-password"
fortigate_host: "192.168.1.99"
fortigate_user: "admin"
fortigate_password: "your-password"
```

> **Optional:** Encrypt with Ansible Vault: `./scripts/setup_vault.sh`

### 4. Start the app

```bash
./start-app.sh
```

On Windows: double-click `Start-App.bat` instead (requires WSL2).

First run pulls the image from ghcr.io, then starts the container.
Open **http://localhost:5173** in your browser.

---

## Docker Image Workflow

A single all-in-one image (`ghcr.io/arunprasade/netconfig:latest`) contains Python, Node.js, Ansible, FastAPI, and React. **Docker Hub is not required** — the image is pulled from ghcr.io.

### On WSL2 — Build and push image (when dependencies change)

```bash
./push-images.sh        # builds image + pushes to ghcr.io
```

Or manually:
```bash
docker compose build    # build image locally (requires Docker Hub for ubuntu:22.04 base)
docker compose push     # push to ghcr.io
```

### On Mac — Pull and run (daily use)

```bash
./start-app.sh          # auto-pulls from ghcr.io if image missing, then starts
```

Or manually:
```bash
docker compose pull     # pull latest image from ghcr.io
docker compose up       # start
```

### When do I need to rebuild the image?

| Change type | Example | Needs image rebuild? | How to share |
|------------|---------|---------------------|-------------|
| Source code | Edit `backend/main.py`, React components | **No** — volume mounted, hot-reloads | `git push` |
| Playbooks / configs | Edit `inventory.yml`, `host_vars/` | **No** — volume mounted | `git push` |
| Python dependencies | Add package to `requirements.txt` | **Yes** | `./push-images.sh` on WSL2 |
| Node dependencies | Add package to `frontend/package.json` | **Yes** | `./push-images.sh` on WSL2 |
| Dockerfile changes | Modify `Dockerfile` | **Yes** | `./push-images.sh` on WSL2 |

Day-to-day code changes work on any machine without rebuilding the image. Only dependency or Dockerfile changes (which are rare) need the build-push-pull cycle.

---

## WSL2-Specific Steps

On a fresh WSL2 environment, you may hit a Docker credential store error:
```
error getting credentials - err: fork/exec docker-credential-desktop.exe: exec format error
```

Fix it once with:
```bash
echo '{}' > ~/.docker/config.json
```

---

## Daily Use

```bash
./start-app.sh          # start (pulls image if needed)
# Ctrl+C to stop

docker compose down     # stop and remove container
docker compose up       # restart without pulling
docker compose logs -f  # stream logs
```

---

## Supported Devices

| Group | Device | Connection |
|-------|--------|------------|
| `nxos`, `vswitch` | Cisco NX-OS | network_cli |
| `ios` | Cisco IOS | network_cli |
| `cumulus` | Cumulus Linux | ssh |
| `fortigate` | FortiGate | SSH (Python/Paramiko) |

### Test without real devices

The `sandbox` host is pre-configured to use Cisco's free public DevNet NX-OS sandbox:
- Host: `sbx-nxos-mgmt.cisco.com`
- Credentials: set in `playbooks/group_vars/all.yml` (check DevNet portal for current password)

---

## Adding a New Device

Use the web UI: click **Add Host**, fill in hostname, group, and IP.

Or manually:
1. Add to `playbooks/inventory.yml` under the appropriate group
2. Create `playbooks/host_vars/<hostname>.yml` with `ansible_host: <IP>`

---

## Output Files

| Location | Contents |
|----------|----------|
| `output/configs/` | Collected configurations — `{hostname}_{timestamp}.json` |
| `output/changes/` | Diff files (only created when changes detected) — `{hostname}_change_{timestamp}.diff` |
| `output/logs/` | Ansible playbook logs — `{hostname}_{timestamp}.log` |

---

## CLI Usage (without the web UI)

```bash
# Run inside the container
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-app \
  python3 scripts/orchestrator.py --host sandbox

# All hosts
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-app \
  python3 scripts/orchestrator.py
```

---

## URLs

| URL | Description |
|-----|-------------|
| http://localhost:5173 | Web UI |
| http://localhost:8000 | Backend API |
| http://localhost:8000/docs | Interactive API docs (Swagger) |

---

## Architecture

```
browser
  └── http://localhost:5173
        └── [single container] React + Vite + FastAPI + Ansible
              ├── Vite dev server (:5173) — proxies /api/* → localhost:8000
              ├── FastAPI + uvicorn (:8000)
              └── Ansible → SSH → network devices
```

Image: `ghcr.io/arunprasade/netconfig:latest` (Ubuntu 22.04 + Python + Node.js + Ansible)

See `CLAUDE.md` for full technical documentation.
