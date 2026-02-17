# Network Configuration Backup System

Multi-vendor network configuration backup and change tracking system.
Collects running configs from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate devices,
detects changes, and generates diff reports. Includes a web UI (React + FastAPI) and CLI.

---

## Prerequisites

The **only** host-level requirement is a running Docker Engine with `docker compose`.
No Python, Node.js, or Ansible needed on your machine — everything runs inside containers.

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

## First-Time Setup (any machine)

### 1. Clone the repo

```bash
git clone git@github.com:ArunPrasadE/network-config-mgmt.git
cd network-config-mgmt
git checkout docker-compose
```

### 2. Create credentials file

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

> **Optional:** Encrypt it with Ansible Vault so credentials aren't stored in plaintext:
> ```bash
> ./scripts/setup_vault.sh
> ```

### 3. Start the app

```bash
./start-app.sh
```

On Windows: double-click `Start-App.bat` instead (requires WSL2).

Wait ~30 seconds on first run while Docker builds the images and installs Node packages.
Then open **http://localhost:5173** in your browser.

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
./start-app.sh          # start everything (builds if needed)
# Ctrl+C to stop

docker compose down     # stop and remove containers
docker compose up       # start without rebuilding (faster)
docker compose up --build   # force rebuild after Dockerfile/dependency changes
```

Logs:
```bash
docker compose logs -f           # all services, live
docker compose logs -f backend   # backend only
docker compose logs -f frontend  # frontend only
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
# Run inside the backend container
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-backend \
  python3 scripts/orchestrator.py --host sandbox

# All hosts
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-backend \
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
        └── [frontend container] React + Vite
              └── /api/* proxy → http://backend:8000 (Docker internal network)
                    └── [backend container] FastAPI + Ansible
                          └── SSH → network devices
```

See `CLAUDE.md` for full technical documentation.
