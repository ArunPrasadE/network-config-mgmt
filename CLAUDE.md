# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-vendor network configuration backup and change tracking system. Uses Ansible playbooks to gather running configurations from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate firewalls. Automatically detects configuration changes and generates diff reports.

## Directory Structure

```
NetworkAutomation/
├── .claude/skills/           # Claude Code skills
│   ├── close-project/        # End-of-session: update docs + commit to front-end
│   ├── update-claude-md/     # Skill to update this file
│   └── git-setup/            # Skill for git operations
├── backend/                  # FastAPI backend server
│   ├── main.py               # API endpoints
│   └── requirements.txt      # Backend Python dependencies
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx           # Main application component
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css         # Global styles (Tailwind)
│   │   └── components/
│   │       ├── AddHostModal.jsx     # Modal for adding new hosts
│   │       ├── ConfigDashboard.jsx  # Parsed config sections display
│   │       ├── DiffViewer.jsx       # Visual diff with highlighting
│   │       ├── HostSelector.jsx     # Dropdown for host selection
│   │       └── LogsModal.jsx        # Log viewer with error highlighting
│   ├── package.json          # Node dependencies
│   └── vite.config.js        # Vite configuration
├── playbooks/
│   ├── gather_configs.yml    # Main playbook (all device types)
│   ├── inventory.yml         # Host inventory
│   ├── group_vars/           # Connection settings + credentials (vault-encrypted)
│   └── host_vars/            # Per-host overrides
├── scripts/
│   ├── orchestrator.py       # Main execution script
│   ├── fortigate_ssh.py      # FortiGate SSH config retrieval
│   └── setup_vault.sh        # Vault encryption setup helper
├── output/
│   ├── configs/              # Collected device configs
│   ├── changes/              # Diff files when changes detected
│   └── logs/                 # Playbook execution logs
├── docs/                     # Technical documentation
├── Start-App.bat             # Windows one-click launcher (double-click to start)
├── start-app.sh              # Full app startup script (Docker + frontend + browser)
├── start-dev.sh              # Start both frontend and backend (local Python)
├── start-backend.sh          # Start FastAPI backend only (local Python)
├── start-frontend.sh         # Start React frontend only
├── Dockerfile                # Container definition
├── ansible.cfg               # Ansible configuration
├── requirements.txt          # Python dependencies
└── .env.example              # Credentials template
```

## Git Branches

- `main` - Current simplified structure
- `front-end` - Web UI development branch
- `archives-v1-v4` - Original versions v1-v5 preserved for reference

## Commands

### Quick Start (One-Click Launch)

The easiest way to start the full application on Windows with WSL:

1. Make sure Docker Desktop is running
2. Double-click `Start-App.bat` in Windows Explorer

This will:
- Start the Docker container (`netconfig-backend`)
- Wait for the backend API to be ready
- Start the React frontend
- Open http://localhost:5173 in your default browser

**From WSL terminal:**
```bash
cd /mnt/d/NetworkMgmt/network-config-mgmt
./start-app.sh
```

### Web Frontend (Development)

```bash
# Start both backend and frontend
./start-dev.sh

# Or start separately:
./start-backend.sh   # FastAPI on http://localhost:8000
./start-frontend.sh  # React on http://localhost:5173
```

The web frontend provides:
- Host selection dropdown with all configured hosts
- Add new hosts form (updates inventory.yml and host_vars)
- RUN button to collect configuration from selected host
- Dashboard with parsed config sections (expandable)
- Visual diff highlighting for changed configurations
- Logs popup with error highlighting

API documentation available at http://localhost:8000/docs

### Run Configuration Backup (CLI)

```bash
# Run for all hosts
python scripts/orchestrator.py

# Run with Ansible Vault
python scripts/orchestrator.py --vault-password-file vault_password.txt

# Run for single host
python scripts/orchestrator.py --host sandbox

# Run with git auto-commit
python scripts/orchestrator.py --git
```

### Docker

```bash
# Build image
docker build -t network-config-mgmt .

# Run backend API server in Docker (first time)
docker run -d --name netconfig-backend -p 8000:8000 \
  -v $(pwd):/app -w /app \
  network-config-mgmt python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Start existing container (after reboot or stop)
docker start netconfig-backend

# Run orchestrator directly in Docker (with host key checking disabled)
docker exec -e ANSIBLE_HOST_KEY_CHECKING=False netconfig-backend \
  python3 scripts/orchestrator.py --host sandbox

# Run container interactively
docker run -it --name netbackup network-config-mgmt bash

# Stop and remove container
docker stop netconfig-backend && docker rm netconfig-backend

# View container logs
docker logs netconfig-backend
```

**Note**: The `ANSIBLE_HOST_KEY_CHECKING=False` environment variable is required because the Docker container's `/app` directory is world-writable, causing Ansible to ignore `ansible.cfg`.

### Ansible Vault

```bash
# Initial setup (encrypt credentials)
./scripts/setup_vault.sh

# Edit encrypted credentials
ansible-vault edit playbooks/group_vars/all.yml --vault-password-file vault_password.txt

# Run playbook manually
ansible-playbook playbooks/gather_configs.yml --vault-password-file vault_password.txt
```

### Cron Setup (inside container)

```bash
# Edit crontab
crontab -e

# Run every 5 minutes
*/5 * * * * cd /app && python3 scripts/orchestrator.py --vault-password-file vault_password.txt >> /var/log/netbackup.log 2>&1
```

## Architecture

### Orchestrator Flow

1. Extract hosts from `inventory.yml` using `ansible-inventory`
2. Run `gather_configs.yml` playbook per host
3. Compare new config with previous baseline
4. If changed: create diff file, remove old config, keep new as baseline
5. If identical: remove new config (no changes)
6. Optional: commit and push to git

### Supported Devices

| Group | Device Type | Connection |
|-------|-------------|------------|
| nxos | Cisco NX-OS switches | network_cli |
| vswitch | Cisco NX-OS virtual switches | network_cli |
| ios | Cisco IOS switches | network_cli |
| cumulus | Cumulus Linux switches | ssh |
| fortigate | FortiGate firewalls | SSH via Python script |

### Credentials Management

Credentials are stored in `playbooks/group_vars/all.yml` and should be encrypted with Ansible Vault:

```yaml
ansible_user: admin
ansible_password: "your-password"
fortigate_host: "192.168.1.99"
fortigate_user: "admin"
fortigate_password: "your-password"
```

FortiGate script reads from environment variables: `FORTIGATE_HOST`, `FORTIGATE_USER`, `FORTIGATE_PASSWORD`

## File Naming Convention

All config files use standardized naming:
```
{hostname}_{YYYY-MM-DD_HH-MM-SS}.json
```

Diff files:
```
{hostname}_change_{YYYY-MM-DD_HH-MM-SS}.diff
```

## Dependencies

### Backend (Python)
- paramiko, python-dotenv
- fastapi, uvicorn, pyyaml, pydantic
- Ansible Collections: cisco.nxos, cisco.ios, ansible.netcommon

### Frontend (Node.js)
- react, react-dom
- vite, tailwindcss
- lucide-react (icons)

### System
- Node.js >= 18 (install via nvm: `nvm install 20`)
- Python >= 3.8
- Docker Desktop (for containerized deployment)
- jq, bat (optional, for diff display)

## Test Environment

### Cisco DevNet Sandbox (Always-On NX-OS)
The `sandbox` host is configured to connect to Cisco's public DevNet sandbox:
- **Host**: sbx-nxos-mgmt.cisco.com
- **Credentials**: Stored in `playbooks/group_vars/all.yml`
- **Device**: Cisco Nexus 9000v (NX-OS 10.3)

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/hosts` | GET | List all configured hosts |
| `/api/groups` | GET | List device groups |
| `/api/hosts` | POST | Add new host |
| `/api/run/{hostname}` | POST | Trigger config collection |
| `/api/jobs/{job_id}` | GET | Get job status |
| `/api/configs/{hostname}/latest` | GET | Get latest config with parsed sections |
| `/api/changes/{hostname}/latest` | GET | Get latest diff |
| `/api/logs/{hostname}/latest` | GET | Get latest log |
| `/api/dashboard/summary` | GET | Dashboard statistics |

## Frontend Configuration

The React frontend uses Vite with a proxy configuration (`vite.config.js`):
- Frontend runs on `http://localhost:5173`
- API calls to `/api/*` are proxied to `http://localhost:8000`
- This allows the frontend and backend to run on different ports during development
