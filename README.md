# Network Configuration Backup System

Multi-vendor network configuration backup and change tracking system using Docker and Ansible.

## Features

- Collects running configurations from multiple network device types
- Detects configuration changes and generates diff reports
- Supports Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate firewalls
- Secure credential storage with Ansible Vault
- Docker containerization for easy deployment
- Optional Git integration for version control

## Quick Start

### 1. Clone and Setup

```bash
cd NetworkAutomation

# Copy and edit environment template
cp .env.example .env
# Edit .env with your credentials

# Setup Ansible Vault (encrypts credentials)
./scripts/setup_vault.sh
```

### 2. Configure Inventory

Edit `playbooks/inventory.yml` to add your devices:

```yaml
all:
  children:
    nxos:
      hosts:
        my-nexus-switch:
    ios:
      hosts:
        my-ios-switch:
```

Add host-specific variables in `playbooks/host_vars/`:

```yaml
# playbooks/host_vars/my-nexus-switch.yml
ansible_host: 192.168.1.10
```

### 3. Run

```bash
# Run directly
python scripts/orchestrator.py --vault-password-file vault_password.txt

# Or with Docker
docker build -t network-config-backup .
docker run -it network-config-backup
```

## Supported Devices

| Device Type | Ansible Group | Connection Method |
|------------|---------------|-------------------|
| Cisco NX-OS | `nxos`, `vswitch` | network_cli |
| Cisco IOS | `ios` | network_cli |
| Cumulus Linux | `cumulus` | ssh |
| FortiGate | `fortigate` | SSH (Python script) |

## Output

- **Configs**: `output/configs/{hostname}_{timestamp}.json`
- **Changes**: `output/changes/{hostname}_change_{timestamp}.diff`
- **Logs**: `output/logs/{hostname}_{timestamp}.log`

## Documentation

See `CLAUDE.md` for detailed technical documentation.

## License

Internal use only.
