# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Network automation framework for collecting and tracking configuration changes across multi-vendor network devices. Uses Ansible playbooks to gather running configurations from Cisco NX-OS, Cisco IOS, Cumulus Linux, and FortiGate firewalls, then compares configs over time to detect and report changes.

## Architecture

### Directory Structure

- `playbook-files/inv_mgmt_playbook_v5-added-git-push/` - Current active playbook version
  - `show_run_each.yml` - Main Ansible playbook with per-device-type plays
  - `inventory_2.yml` - Ansible inventory defining host groups (nxos, ios, vswitch, cumulus, local)
  - `group_vars/` - Connection settings per device type (ansible_connection, credentials)
  - `host_vars/` - Per-host variable overrides
  - `python_scripts/` - Helper scripts including FortiGate SSH config retrieval
  - `running_config/` - Output directory for collected device configs
  - `changes/` - Output directory for diff files when changes detected
  - `logs/` - Per-host playbook execution logs
- `playbook-files/archives/` - Previous playbook versions (v1-v4)
- `documentations/` - Technical documentation for scripts and playbooks

### Playbook Structure

The main playbook (`show_run_each.yml`) contains separate plays for each device type:
- **vswitch/nxos**: Uses `cisco.nxos.nxos_command` for NX-OS switches
- **ios**: Uses `cisco.ios.ios_command` for IOS switches
- **cumulus**: Uses `ansible.builtin.command` with become for Linux-based switches
- **fortigate**: Runs Python script via `local` host group for SSH-based config retrieval

Each play gathers multiple show commands and writes combined output to timestamped files.

### Shell Script Workflow

`run_playbook_v2.sh` orchestrates the automation:
1. Extracts hosts dynamically from inventory using `ansible-inventory` + `jq`
2. Runs playbook per-host with output to timestamped log files
3. Calls `diff_and_cleanup()` function to compare latest two configs
4. Filters out timestamp lines before comparison
5. If different: creates diff file, deletes old config (keeps new as baseline)
6. If identical: deletes new config file (no change)

## Commands

### Build Docker Image
```sh
# ARM architecture
docker buildx build --platform linux/arm64 -t jpc1-mgmt:v.1 .

# AMD architecture
docker buildx build --platform linux/amd64 -t jpc1-mgmt:v.1 .
```

### Create and Run Container
```sh
docker run -it --name container-name jpc1-mgmt:v.1
```

### Run Playbook (inside container)
```sh
# Make script executable first
chmod +x /inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh

# Manual execution
/inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh

# Via cron (e.g., every 5 minutes)
*/5 * * * * /inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh
```

### Run Playbook for Single Host
```sh
ansible-playbook /inv_mgmt_playbook/show_run_each.yml -i /inv_mgmt_playbook/inventory_2.yml --limit hostname
```

## Dependencies

- Ansible with collections: `cisco.nxos`, `cisco.ios`
- Python packages: `paramiko` (for FortiGate SSH)
- System tools: `jq`, `bat` (batcat for diff display)

## Device Group Credentials

Connection settings are in `group_vars/`:
- `ansible_connection`: `ansible.netcommon.network_cli` for network devices
- `ansible_network_os`: Device OS type (nxos, ios, etc.)
- Credentials stored in group_vars files (note: credentials are currently in plaintext)
