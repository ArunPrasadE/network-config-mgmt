# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-vendor network configuration backup and change tracking system. Collects running configs from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate devices via Ansible. Detects changes and generates diff reports. Includes a FastAPI backend and React frontend for interactive use.

## Git Branches

- `main` - Current structure (backend + frontend + CLI)
- `front-end` - Web UI development branch
- `archives-v1-v4` - Original versions v1-v5 preserved for reference

## Commands

### Quick Start (Windows/WSL)

1. Ensure Docker Desktop is running
2. Double-click `Start-App.bat` in Windows Explorer, **or** from WSL terminal:

```bash
./start-app.sh   # Builds Docker image, starts backend, launches frontend, opens browser
```

### Development (Local Python, no Docker)

```bash
./start-dev.sh        # Start both backend (port 8000) and frontend (port 5173)
./start-backend.sh    # FastAPI only — creates venv, installs deps, runs uvicorn
./start-frontend.sh   # React only — npm install + vite dev
```

API docs (Swagger): http://localhost:8000/docs

### CLI Configuration Backup

```bash
python scripts/orchestrator.py                                    # All hosts
python scripts/orchestrator.py --host sandbox                     # Single host
python scripts/orchestrator.py --vault-password-file vault.txt    # With Vault
python scripts/orchestrator.py --git                              # Auto-commit to Git
```

### Docker

```bash
docker build -t network-config-mgmt .

# First-time run (mounts project dir)
docker run -d --name netconfig-backend -p 8000:8000 \
  -v $(pwd):/app -w /app \
  network-config-mgmt python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

docker start netconfig-backend   # Start existing container

# Run orchestrator inside container — env var required (world-writable /app causes ansible.cfg to be ignored)
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-backend \
  python3 scripts/orchestrator.py --host sandbox

docker logs netconfig-backend
docker stop netconfig-backend && docker rm netconfig-backend
```

### Ansible Vault

```bash
./scripts/setup_vault.sh                                              # Initial encryption setup
ansible-vault edit playbooks/group_vars/all.yml --vault-password-file vault_password.txt
ansible-playbook playbooks/gather_configs.yml --vault-password-file vault_password.txt
```

### Cron (inside container)

```
*/5 * * * * cd /app && python3 scripts/orchestrator.py --vault-password-file vault_password.txt >> /var/log/netbackup.log 2>&1
```

## Architecture

### Three-Tier Stack

```
React frontend (5173) → Vite proxy /api/* → FastAPI backend (8000) → Ansible + scripts → Devices
```

Vite proxies all `/api/*` requests to `http://localhost:8000` (configured in `frontend/vite.config.js`).

### Async Job Execution

Config collection is long-running. The backend uses a non-blocking pattern:
1. `POST /api/run/{hostname}` → spawns `orchestrator.py --host {hostname}` as asyncio subprocess, returns `job_id` immediately
2. Frontend polls `GET /api/jobs/{job_id}` every 2 seconds
3. Job status is tracked in `running_jobs` dict (in-memory; lost on restart)
4. On completion, frontend fetches `/api/configs/{hostname}/latest` and `/api/changes/{hostname}/latest`

### Config Change Detection (`scripts/orchestrator.py`)

1. Collect new config via Ansible → write to `output/configs/{hostname}_{timestamp}.json`
2. Compare with previous baseline file (second-to-last by timestamp)
3. Strip time-sensitive lines (NTP counters, etc.) before diffing
4. **Changed**: create unified diff in `output/changes/`, delete old baseline, keep new as baseline
5. **Identical**: delete new file; baseline unchanged

### Multi-Vendor Playbook (`playbooks/gather_configs.yml`)

Single playbook with four plays, each targeting a device group:
- `nxos` / `vswitch` → `cisco.nxos.nxos_command`
- `ios` → `cisco.ios.ios_command`
- `cumulus` → `ansible.builtin.command` (SSH)
- `fortigate` → `ansible.builtin.script` runs `scripts/fortigate_ssh.py` on localhost via Paramiko

FortiGate credentials are passed as env vars: `FORTIGATE_HOST`, `FORTIGATE_USER`, `FORTIGATE_PASSWORD` (sourced from `group_vars/all.yml`).

### Supported Device Groups

| Group | Device | Connection |
|-------|--------|------------|
| nxos | Cisco NX-OS | network_cli |
| vswitch | Cisco NX-OS virtual | network_cli |
| ios | Cisco IOS | network_cli |
| cumulus | Cumulus Linux | ssh |
| fortigate | FortiGate | Paramiko script (localhost) |

### Credentials

Stored in `playbooks/group_vars/all.yml` — encrypt with Ansible Vault before committing:
```yaml
ansible_user: admin
ansible_password: "..."
fortigate_host: "192.168.1.99"
fortigate_user: "admin"
fortigate_password: "..."
```

### File Naming

```
output/configs/   {hostname}_{YYYY-MM-DD_HH-MM-SS}.json
output/changes/   {hostname}_change_{YYYY-MM-DD_HH-MM-SS}.diff
output/logs/      {hostname}_{YYYY-MM-DD_HH-MM-SS}.log
```

One baseline config file per host is kept; diff files only appear when changes are detected.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hosts` | List all configured hosts |
| POST | `/api/hosts` | Add host (updates `inventory.yml` + creates `host_vars/`) |
| GET | `/api/groups` | List device groups |
| POST | `/api/run/{hostname}` | Trigger config collection (returns `job_id`) |
| GET | `/api/jobs/{job_id}` | Poll job status |
| GET | `/api/configs/{hostname}/latest` | Latest config with parsed sections |
| GET | `/api/changes/{hostname}/latest` | Latest diff (additions/removals) |
| GET | `/api/logs/{hostname}/latest` | Latest log with error extraction |
| GET | `/api/dashboard/summary` | Dashboard statistics |

## Test Environment

**Cisco DevNet Always-On NX-OS Sandbox** (configured as `sandbox` host):
- Host: `sbx-nxos-mgmt.cisco.com`
- Device: Cisco Nexus 9000v (NX-OS 10.3)
- Credentials: `playbooks/group_vars/all.yml`

## Dependencies

**Python** (`requirements.txt`): `ansible`, `paramiko`, `fastapi`, `uvicorn`, `pyyaml`, `pydantic`, `python-dotenv`

**Ansible Collections**: `cisco.nxos`, `cisco.ios`, `ansible.netcommon`, `fortinet.fortios`

**Node.js** (`frontend/package.json`): React 18, Vite 5, Tailwind CSS 3, lucide-react

**System**: Python >= 3.8, Node.js >= 18 (`nvm install 20`), Docker Desktop

## Claude Code Skills

- `.claude/skills/git-setup/` — Git SSH setup + commit/push
- `.claude/skills/update-claude-md/` — Update this file after changes
- `.claude/skills/close-project/` — End-of-session: update docs + commit to front-end branch
