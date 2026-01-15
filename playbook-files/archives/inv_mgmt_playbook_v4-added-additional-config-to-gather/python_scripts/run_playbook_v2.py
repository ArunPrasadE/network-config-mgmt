#!/usr/bin/env python3

import os
import subprocess
import glob
import shutil
import tempfile
import time
from datetime import datetime

# --- Configuration ---
INVENTORY = "/inv_mgmt_playbook/inventory_2.yml"
PLAYBOOK = "/inv_mgmt_playbook/show_run_each.yml"
LOG_DIR = "/inv_mgmt_playbook/logs"
CONFIG_DIR = "/inv_mgmt_playbook/running_config"
CHANGES_DIR = "/inv_mgmt_playbook/changes"
IGNORE_PATTERNS = r'^!Time:|^!Running configuration last done at:'

# --- Ensure directories exist ---
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CHANGES_DIR, exist_ok=True)

# --- Helper Functions ---

def get_hosts_from_inventory():
    """Fetch the list of hosts from the Ansible inventory using ansible-inventory and jq."""
    try:
        result = subprocess.run(
            [
                "ansible-inventory", "-i", INVENTORY, "--list"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        # Use jq to parse the output
        jq_cmd = [
            "jq", "-r",
            "to_entries[] | select(.value.hosts) | .value.hosts[]"
        ]
        jq_proc = subprocess.run(
            jq_cmd,
            input=result.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        hosts = sorted(set(jq_proc.stdout.strip().splitlines()))
        return hosts
    except subprocess.CalledProcessError as e:
        print("Error fetching hosts from inventory:", e)
        return []

def run_playbook_for_host(host, ansible_date_time):
    """Run the Ansible playbook for a specific host and log output."""
    log_file = os.path.join(LOG_DIR, f"{host}_{ansible_date_time}.log")
    cmd = [
        "ansible-playbook", PLAYBOOK,
        "-i", INVENTORY,
        "--limit", host
    ]
    with open(log_file, "w") as logf:
        result = subprocess.run(cmd, stdout=logf, stderr=subprocess.STDOUT)
    return result.returncode, log_file

def config_file_exists(host, ansible_date_time):
    """Check if the config file was created for this host."""
    config_file = os.path.join(CONFIG_DIR, f"{host}_{ansible_date_time}.json")
    return os.path.isfile(config_file), config_file

def filter_config_file(src, ignore_patterns):
    """Return a temp file path with lines matching ignore_patterns removed."""
    temp_fd, temp_path = tempfile.mkstemp()
    with open(src, "r") as infile, os.fdopen(temp_fd, "w") as outfile:
        for line in infile:
            if not re.search(ignore_patterns, line):
                outfile.write(line)
    return temp_path

def diff_and_cleanup(host):
    """Compare the two most recent config files for a host, ignoring time lines, and manage diffs."""
    files = sorted(glob.glob(os.path.join(CONFIG_DIR, f"{host}_*.json")))
    num_files = len(files)
    print(f"Host: {host}\n")
    if num_files < 2:
        print("  Not enough files to compare.\n")
        return

    prev_file = files[-2]
    new_file = files[-1]
    print(f"  Previous: {os.path.basename(prev_file)}\n")
    print(f"  New:      {os.path.basename(new_file)}\n")

    # Filter out ignored lines
    import re
    prev_tmp = filter_config_file(prev_file, IGNORE_PATTERNS)
    new_tmp = filter_config_file(new_file, IGNORE_PATTERNS)

    # Compare files
    diff_cmd = ["diff", "-q", prev_tmp, new_tmp]
    diff_result = subprocess.run(diff_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if diff_result.returncode != 0:
        print("  Files are DIFFERENT! Writing diff report and updating baseline.\n")
        diff_file = os.path.join(
            CHANGES_DIR,
            f"{host}_change_{os.path.basename(new_file)[:-5]}.diff"
        )
        with open(diff_file, "w") as df:
            df.write(f"Diff for {host} at {os.path.basename(new_file)[:-5]}:\n")
            # Write unified diff
            diff_u_cmd = ["diff", "-u", prev_tmp, new_tmp]
            subprocess.run(diff_u_cmd, stdout=df)
        print(f"  Diff written to: {diff_file}\n")
        # Remove the old file, keep the new one as the new baseline
        os.remove(prev_file)
        print(f"  Old file deleted: {os.path.basename(prev_file)}\n")
    else:
        print("  Files are IDENTICAL (ignoring time lines). Deleting new file.\n")
        os.remove(new_file)
        print(f"  Deleted: {os.path.basename(new_file)}\n")

    # Clean up temp files
    os.remove(prev_tmp)
    os.remove(new_tmp)

def show_latest_diff(host):
    """Show the most recent diff file for the host if it was created in the last 2 minutes."""
    pattern = os.path.join(CHANGES_DIR, f"{host}_change_*.diff")
    diff_files = sorted(
        glob.glob(pattern),
        key=lambda x: os.path.getmtime(x),
        reverse=True
    )
    if not diff_files:
        print("\nDiff file not created.\n")
        return
    latest_diff = diff_files[0]
    # Check if the diff file is recent (within 2 minutes)
    if os.path.getmtime(latest_diff) >= time.time() - 120:
        print(f"\nDiff file created: {os.path.basename(latest_diff)}\n")
        print("Diff results:")
        try:
            subprocess.run(["batcat", latest_diff])
        except FileNotFoundError:
            # Fallback to cat if batcat is not available
            subprocess.run(["cat", latest_diff])
        print()
    else:
        print("\nDiff file not created.\n")

# --- Main Script ---

import re

def main():
    ansible_date = datetime.now().strftime("%Y-%m-%d")
    ansible_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    hosts = get_hosts_from_inventory()
    print("Hosts found:\n")
    print("\n".join(hosts))
    print("\nRunning playbook for each host...\n")

    for host in hosts:
        # Run playbook
        retcode, log_file = run_playbook_for_host(host, ansible_date_time)
        if retcode != 0:
            print(f"\nError executing playbook for {host}. Check the log file for details.\n")
        else:
            print(f"\nPlaybook executed successfully for {host}.\n")

        # Check config file
        exists, config_file = config_file_exists(host, ansible_date_time)
        if exists:
            print(f"\nRunning config file created for {host}.\n")
            print(f"{os.path.basename(config_file)}\n")
            print(f"Log file: {log_file}\n")
        else:
            print(f"\nRunning config file not created for {host}.\n")
            print(f"Log file: {log_file}\n")

        # Run diff and cleanup
        print("\nRunning diff and cleanup script...\n")
        diff_and_cleanup(host)

        # Show latest diff if created
        show_latest_diff(host)

if __name__ == "__main__":
    main()
