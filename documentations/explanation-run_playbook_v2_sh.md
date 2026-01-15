
---

# Technical Documentation: `run_playbook_v2.sh`

## Overview

The `run_playbook_v2.sh` script automates the process of running an Ansible playbook against a set of network devices, collecting their running configurations, and tracking configuration changes over time. It logs all actions, compares new configurations with previous ones, and generates diff reports for any detected changes.

---

## Table of Contents

- [Technical Documentation: `run_playbook_v2.sh`](#technical-documentation-run_playbook_v2sh)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [1. Variable Definitions](#1-variable-definitions)
  - [2. Directory Preparation](#2-directory-preparation)
  - [3. Function: diff\_and\_cleanup](#3-function-diff_and_cleanup)
  - [4. Host Discovery](#4-host-discovery)
  - [5. Date and Time Variables](#5-date-and-time-variables)
  - [6. Main Execution Loop](#6-main-execution-loop)
    - [6.1. Playbook Execution](#61-playbook-execution)
      - [Playbook Success Check](#playbook-success-check)
    - [6.2. Config File Verification](#62-config-file-verification)
    - [6.3. Diff and Cleanup](#63-diff-and-cleanup)
    - [6.4. Diff File Reporting](#64-diff-file-reporting)
  - [7. End of Script](#7-end-of-script)
  - [Summary](#summary)
  - [Prerequisites](#prerequisites)

---

## 1. Variable Definitions

```bash
INVENTORY="/inv_mgmt_playbook/inventory_2.yml"
PLAYBOOK="/inv_mgmt_playbook/show_run_each.yml"
LOG_DIR="/inv_mgmt_playbook/logs"
CONFIG_DIR="/inv_mgmt_playbook/running_config"
CHANGES_DIR="/inv_mgmt_playbook/changes"
```

- **INVENTORY**: Path to the Ansible inventory file.
- **PLAYBOOK**: Path to the Ansible playbook to be executed.
- **LOG_DIR**: Directory for storing log files.
- **CONFIG_DIR**: Directory for storing running configuration files.
- **CHANGES_DIR**: Directory for storing diff files (configuration changes).

---

## 2. Directory Preparation

```bash
mkdir -p "$LOG_DIR"
mkdir -p "$CHANGES_DIR"
```

- Ensures that the log and changes directories exist. If they do not, they are created.

---

## 3. Function: diff_and_cleanup

```bash
diff_and_cleanup() {
    local HOST="$1"
    local IGNORE_PATTERNS='^!Time:|^!Running configuration last done at:'
    ...
}
```

- **Purpose**: Compares the two most recent configuration files for a given host, ignoring lines that match timestamp patterns.
- **IGNORE_PATTERNS**: Regular expression to filter out lines that should not be considered in the diff (e.g., timestamps).

**Function Steps:**
- Lists and sorts all config files for the host.
- If fewer than two files exist, exits the function.
- Identifies the previous and new config files.
- Filters out ignored lines using `grep -Ev`.
- Compares the filtered files:
    - If different: Generates a diff report, deletes the old file, and keeps the new one as the baseline.
    - If identical: Deletes the new file (no change detected).
- Cleans up temporary files.

---

## 4. Host Discovery

```bash
HOSTS=$(/bin/ansible-inventory -i "$INVENTORY" --list | jq -r '
  to_entries[]
  | select(.value.hosts)
  | .value.hosts[]
' | sort -u)
```

- Uses `ansible-inventory` and `jq` to dynamically extract all hostnames from the inventory file.
- The resulting list is sorted and deduplicated.

---

## 5. Date and Time Variables

```bash
ANSIBLE_DATE=$(date +%Y-%m-%d)
ANSIBLE_DATE_TIME=$(date +%Y-%m-%d_%H-%M-%S)
```

- **ANSIBLE_DATE**: Current date in `YYYY-MM-DD` format.
- **ANSIBLE_DATE_TIME**: Current date and time in `YYYY-MM-DD_HH-MM-SS` format.
- These variables are used for timestamping output files.

---

## 6. Main Execution Loop

### 6.1. Playbook Execution

```bash
for HOST in $HOSTS; do
    /bin/ansible-playbook "$PLAYBOOK" -i "$INVENTORY" --limit "$HOST" > "$LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log" 2>&1
    ...
done
```

- Iterates over each host.
- Runs the Ansible playbook for the specific host, logging all output to a host- and time-specific log file.

#### Playbook Success Check

```bash
if [ $? -ne 0 ]; then
    echo "Error executing playbook for $HOST. Check the log file for details."
else
    echo "Playbook executed successfully for $HOST."
fi
```

- Checks the exit status of the playbook run and prints a success or error message.

---

### 6.2. Config File Verification

```bash
if [ -f "$CONFIG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.json" ]; then
    echo "Running config file created for $HOST."
    echo "${HOST}_${ANSIBLE_DATE_TIME}.json"
    echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"
else
    echo "Running config file not created for $HOST."
    echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"
fi
```

- Checks if the expected configuration file was created for the host.
- Prints the result and the location of the log file.

---

### 6.3. Diff and Cleanup

```bash
echo "Running diff and cleanup script..."
diff_and_cleanup "$HOST"
```

- Calls the `diff_and_cleanup` function for the current host to compare configurations and manage diffs.

---

### 6.4. Diff File Reporting

```bash
LATEST_DIFF=$(ls -t "$CHANGES_DIR"/${HOST}_change_*.diff 2>/dev/null | head -n1)
if [ -n "$LATEST_DIFF" ] && [ "$(stat -c %Y "$LATEST_DIFF")" -ge $(( $(date +%s) - 120 )) ]; then
    echo "Diff file created: $(basename "$LATEST_DIFF")"
    echo "Diff results:"
    batcat "$LATEST_DIFF"
else
    echo "Diff file not created."
fi
```

- Identifies the most recent diff file for the host.
- If the diff file exists and was modified within the last 2 minutes, prints its name and contents (using `batcat` for syntax highlighting).
- Otherwise, indicates that no diff file was created.

---

## 7. End of Script

```bash
done
```

- Ends the loop over all hosts.

---

## Summary

- **Purpose**: Automates configuration backup and change tracking for network devices using Ansible.
- **Key Features**:
    - Dynamic host discovery from inventory.
    - Per-host, per-run logging.
    - Intelligent config comparison with timestamp filtering.
    - Automated diff reporting and file management.
- **Usage**: Run the script in a shell environment with access to the specified directories and required tools (`ansible`, `jq`, `batcat`).

---

## Prerequisites

- Ansible and its dependencies installed.
- `jq` for JSON parsing.
- `batcat` (optional, for pretty diff output).
- Properly configured inventory and playbook files.
- Sufficient permissions to read/write in the specified directories.

---

**For further customization or troubleshooting, refer to the inline comments in the script or contact the script maintainer.**