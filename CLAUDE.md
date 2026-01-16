# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-vendor network configuration backup and change tracking system. Uses Ansible playbooks to gather running configurations from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate firewalls. Automatically detects configuration changes and generates diff reports.

## Directory Structure

```
NetworkAutomation/
├── .claude/skills/           # Claude Code skills
│   ├── update-claude-md/     # Skill to update this file
│   └── git-setup/            # Skill for git operations
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
├── Dockerfile                # Container definition
├── ansible.cfg               # Ansible configuration
├── requirements.txt          # Python dependencies
└── .env.example              # Credentials template
```

## Git Branches

- `main` - Current simplified structure
- `archives-v1-v4` - Original versions v1-v5 preserved for reference

## Commands

### Run Configuration Backup

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
docker build -t network-config-backup .

# Run container interactively
docker run -it --name netbackup network-config-backup bash

# Run orchestrator with mounted output
docker run --rm -v $(pwd)/output:/app/output network-config-backup python3 scripts/orchestrator.py

# Run for specific host
docker run --rm -v $(pwd)/output:/app/output network-config-backup python3 scripts/orchestrator.py --host <hostname>
```

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

- Python: paramiko, python-dotenv
- Ansible Collections: cisco.nxos, cisco.ios, ansible.netcommon
- System: jq, bat (optional, for diff display)
