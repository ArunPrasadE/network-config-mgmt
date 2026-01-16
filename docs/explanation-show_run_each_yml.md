Certainly! Here is a **technical documentation** for your `show_run_each.yml` Ansible playbook, following the same professional format as before.

---

# Technical Documentation: `show_run_each.yml`

## Overview

The `show_run_each.yml` Ansible playbook automates the collection of running configurations and key operational data from a variety of network devices, including Cisco NX-OS (vswitch), Cisco IOS, Cumulus Linux, and FortiGate firewalls. The playbook is structured to support multiple device types, using device-appropriate modules and commands, and saves the gathered data to host-specific files for later analysis and change tracking.

---

## Table of Contents

- [Technical Documentation: `show_run_each.yml`](#technical-documentation-show_run_eachyml)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [1. Supported Device Types](#1-supported-device-types)
  - [2. General Playbook Structure](#2-general-playbook-structure)
  - [3. Playbook Sections](#3-playbook-sections)
    - [Vswitch (Cisco NX-OS)](#vswitch-cisco-nx-os)
    - [IOS (Cisco IOS)](#ios-cisco-ios)
    - [Cumulus (Cumulus Linux)](#cumulus-cumulus-linux)
    - [FortiGate (FortiGate Firewalls)](#fortigate-fortigate-firewalls)
  - [4. File Output and Naming Conventions](#4-file-output-and-naming-conventions)
  - [5. Prerequisites](#5-prerequisites)
  - [6. Usage Notes](#6-usage-notes)
  - [Example Output File (NX-OS)](#example-output-file-nx-os)

---

## 1. Supported Device Types

- **Vswitch**: Cisco NX-OS switches
- **IOS**: Cisco IOS switches
- **Cumulus**: Cumulus Linux switches
- **FortiGate**: FortiGate firewalls

---

## 2. General Playbook Structure

- Each device type is handled in a separate play.
- Each play:
    - Targets a specific host group.
    - Disables fact gathering by default (`gather_facts: no`).
    - Ignores unreachable hosts and errors to ensure the playbook continues for all devices.
    - Runs a series of tasks to collect configuration and operational data.
    - Writes the output to a uniquely named file per host and per run.

---

## 3. Playbook Sections

### Vswitch (Cisco NX-OS)

**Purpose:**  
Collects running configuration and key operational data from Cisco NX-OS switches.

**Key Tasks:**
- Gathers Ansible facts manually.
- Runs multiple `show` commands using `cisco.nxos.nxos_command`:
    - `show running-config`
    - `show interface status`
    - `show vlan brief`
    - `show port-channel summary`
    - `show ip interface brief`
- Registers the output as `nexus_output`.
- Writes the output to a host-specific file, formatting each command’s output under a clear section header.

**Output File Example:**
```
/inv_mgmt_playbook/running_config/{{ inventory_hostname }}_{{ ansible_date_time.date }}_{{ ansible_date_time.hour }}-{{ ansible_date_time.minute }}-{{ ansible_date_time.second }}.json
```

---

### IOS (Cisco IOS)

**Purpose:**  
Collects running configuration and interface status from Cisco IOS switches.

**Key Tasks:**
- Gathers Ansible facts manually.
- Runs `show running-configuration` and `show interface status` using `cisco.ios.ios_command`.
- Registers the output as `ios_output`.
- Writes the output to a host-specific file, with clear section headers.

**Output File Example:**
```
/inv_mgmt_playbook/running_config/{{ inventory_hostname }}_{{ ansible_date_time.date }}.json
```

---

### Cumulus (Cumulus Linux)

**Purpose:**  
Collects running configuration and interface status from Cumulus Linux switches.

**Key Tasks:**
- Gathers Ansible facts manually.
- Runs `net show configuration commands` and `net show interface` using `ansible.builtin.command` (with privilege escalation via `become: yes`).
- Registers outputs as `cumulus_conf_output` and `cumulus_intf_output`.
- Writes the output to a host-specific file, with clear section headers.
- Uses `delegate_to: localhost` for the file writing task.

**Output File Example:**
```
/config_mgmt_playbook/running_config/{{ inventory_hostname }}_{{ ansible_date_time.date }}.json
```

---

### FortiGate (FortiGate Firewalls)

**Purpose:**  
Collects the full configuration from FortiGate firewalls via SSH.

**Key Tasks:**
- Gathers Ansible facts manually.
- Runs a custom Python script (`fortigate_get_full_config.py`) to retrieve the full configuration.
- Extracts the hostname from the script output using `set_fact` and JMESPath query.
- Writes the configuration to a file named after the device hostname.

**Output File Example:**
```
/fortigate/running_config/{{ fortigate_hostname }}_{{ ansible_date_time.date }}.json
```

---

## 4. File Output and Naming Conventions

- **File Location**: Each device type writes to a specific directory, typically under `/inv_mgmt_playbook/running_config/` or `/fortigate/running_config/`.
- **File Naming**: Files are named using the device hostname and the current date (and time, for NX-OS), ensuring uniqueness and traceability.
- **File Format**: Each file contains clearly delimited sections for each command’s output, making it easy to review or diff configurations.

---

## 5. Prerequisites

- **Ansible Collections**:
    - `cisco.nxos` for NX-OS devices
    - `cisco.ios` for IOS devices
- **Ansible Modules**:
    - `ansible.builtin.setup`
    - `ansible.builtin.command`
    - `ansible.builtin.copy`
    - `ansible.builtin.set_fact`
- **Python script**: For FortiGate, ensure `fortigate_get_full_config.py` is present and executable.
- **Inventory**: Host groups (`vswitch`, `ios`, `cumulus`, `local`) must be defined in your Ansible inventory.
- **Permissions**: Sufficient privileges to run commands on network devices and write to the specified directories.

---

## 6. Usage Notes

- **Error Handling**:  
  The playbook uses `ignore_unreachable: yes` and `ignore_errors: yes` to continue execution even if some devices are unreachable or a task fails.
- **Fact Gathering**:  
  Facts are gathered manually for each device, rather than automatically, to reduce playbook runtime and avoid unnecessary data collection.
- **Output Structure**:  
  Each output file is structured with section headers for each command, making it easy to parse or review.
- **Extensibility**:  
  Additional device types or commands can be added by following the same play structure.

---

## Example Output File (NX-OS)

```
=== Running Configuration ===

<output of show running-config>

=== Interface Status ===

<output of show interface status>

=== VLAN Brief ===

<output of show vlan brief>

=== Port-Channel Summary ===

<output of show port-channel summary>

=== IP Interface Brief ===

<output of show ip interface brief>
```

---

**For further customization or troubleshooting, refer to the inline comments in the playbook or contact the playbook maintainer.**