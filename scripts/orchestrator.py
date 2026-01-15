#!/usr/bin/env python3
"""
Network Configuration Orchestrator

Single Python script that orchestrates the entire config backup workflow:
1. Discovers hosts from Ansible inventory
2. Runs playbook per host to gather configs
3. Compares new configs with previous ones
4. Creates diff reports for changes
5. Optionally commits and pushes to git

Usage:
    python orchestrator.py [--git] [--vault-password-file FILE]
"""

import os
import re
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from difflib import unified_diff

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PLAYBOOK = PROJECT_ROOT / "playbooks" / "gather_configs.yml"
INVENTORY = PROJECT_ROOT / "playbooks" / "inventory.yml"
CONFIG_DIR = PROJECT_ROOT / "output" / "configs"
CHANGES_DIR = PROJECT_ROOT / "output" / "changes"
LOG_DIR = PROJECT_ROOT / "output" / "logs"

# Patterns to ignore in diff (timestamps, etc.)
IGNORE_PATTERNS = [
    r'^!Time:',
    r'^!Running configuration last done at:',
    r'^ntp clock-period',
    r'^! Last configuration change at',
]


def setup_directories():
    """Ensure output directories exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CHANGES_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_hosts():
    """Extract hosts from Ansible inventory."""
    try:
        result = subprocess.run(
            ["ansible-inventory", "-i", str(INVENTORY), "--list"],
            capture_output=True,
            text=True,
            check=True
        )
        inventory = json.loads(result.stdout)

        hosts = set()
        for group, data in inventory.items():
            if isinstance(data, dict) and "hosts" in data:
                hosts.update(data["hosts"])

        return sorted(hosts)
    except subprocess.CalledProcessError as e:
        print(f"Error reading inventory: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing inventory JSON: {e}", file=sys.stderr)
        sys.exit(1)


def run_playbook(host, vault_password_file=None):
    """Run Ansible playbook for a specific host."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_DIR / f"{host}_{timestamp}.log"

    cmd = [
        "ansible-playbook",
        str(PLAYBOOK),
        "-i", str(INVENTORY),
        "--limit", host,
    ]

    if vault_password_file:
        cmd.extend(["--vault-password-file", vault_password_file])

    print(f"\n{'='*60}")
    print(f"Running playbook for: {host}")
    print(f"{'='*60}")

    with open(log_file, "w") as log:
        result = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)

    if result.returncode != 0:
        print(f"  [ERROR] Playbook failed for {host}")
        print(f"  Log file: {log_file}")
        return False

    print(f"  [OK] Playbook succeeded")
    print(f"  Log file: {log_file}")
    return True


def get_config_files(host):
    """Get all config files for a host, sorted by timestamp."""
    pattern = f"{host}_*.json"
    files = sorted(CONFIG_DIR.glob(pattern))
    return files


def filter_ignore_lines(content):
    """Remove lines matching ignore patterns."""
    filtered = []
    for line in content.splitlines():
        skip = False
        for pattern in IGNORE_PATTERNS:
            if re.match(pattern, line):
                skip = True
                break
        if not skip:
            filtered.append(line)
    return "\n".join(filtered)


def diff_and_cleanup(host):
    """Compare configs and manage files."""
    files = get_config_files(host)

    print(f"\n  Comparing configs for {host}...")

    if len(files) < 2:
        print(f"  Not enough config files to compare ({len(files)} found)")
        return None

    prev_file = files[-2]
    new_file = files[-1]

    print(f"  Previous: {prev_file.name}")
    print(f"  New:      {new_file.name}")

    # Read and filter content
    prev_content = filter_ignore_lines(prev_file.read_text())
    new_content = filter_ignore_lines(new_file.read_text())

    if prev_content == new_content:
        print(f"  [IDENTICAL] No changes detected - removing new file")
        new_file.unlink()
        return None

    # Create diff file
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    diff_file = CHANGES_DIR / f"{host}_change_{timestamp}.diff"

    diff_lines = list(unified_diff(
        prev_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=str(prev_file.name),
        tofile=str(new_file.name),
    ))

    with open(diff_file, "w") as f:
        f.write(f"Diff for {host} at {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.writelines(diff_lines)

    print(f"  [CHANGED] Diff written to: {diff_file.name}")

    # Remove old file, keep new as baseline
    prev_file.unlink()
    print(f"  Removed old baseline: {prev_file.name}")

    return diff_file


def display_diff(diff_file):
    """Display diff file content."""
    if not diff_file:
        return

    print(f"\n  {'='*50}")
    print(f"  DIFF CONTENT:")
    print(f"  {'='*50}")

    # Try batcat first, fall back to cat
    if shutil.which("batcat"):
        subprocess.run(["batcat", "--style=plain", str(diff_file)])
    elif shutil.which("bat"):
        subprocess.run(["bat", "--style=plain", str(diff_file)])
    else:
        print(diff_file.read_text())


def git_commit_and_push(host, config_file):
    """Commit and push config changes to git."""
    if not config_file or not config_file.exists():
        return

    try:
        os.chdir(PROJECT_ROOT)

        # Check if git repo exists
        result = subprocess.run(
            ["git", "status"], capture_output=True, text=True
        )
        if result.returncode != 0:
            print("  [WARN] Not a git repository, skipping git push")
            return

        # Add the config file
        subprocess.run(["git", "add", str(config_file)], check=True)

        # Check if there are staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True
        )
        if result.returncode == 0:
            print("  [INFO] No changes to commit")
            return

        # Commit
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"[Auto] Config update for {host} at {timestamp}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
            capture_output=True
        )
        print(f"  [GIT] Committed: {commit_msg}")

        # Push
        result = subprocess.run(
            ["git", "push"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  [GIT] Pushed to remote")
        else:
            print(f"  [WARN] Push failed: {result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Git operation failed: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Network Configuration Orchestrator"
    )
    parser.add_argument(
        "--git",
        action="store_true",
        help="Commit and push changes to git"
    )
    parser.add_argument(
        "--vault-password-file",
        type=str,
        help="Path to Ansible Vault password file"
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Run for specific host only"
    )
    args = parser.parse_args()

    setup_directories()

    print("=" * 60)
    print("Network Configuration Orchestrator")
    print("=" * 60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Config dir:   {CONFIG_DIR}")
    print(f"Changes dir:  {CHANGES_DIR}")
    print(f"Log dir:      {LOG_DIR}")

    # Get hosts
    hosts = get_hosts()
    if args.host:
        if args.host not in hosts:
            print(f"Error: Host '{args.host}' not found in inventory")
            sys.exit(1)
        hosts = [args.host]

    print(f"\nHosts to process: {', '.join(hosts)}")

    # Process each host
    for host in hosts:
        success = run_playbook(host, args.vault_password_file)

        if success:
            # Find the new config file
            config_files = get_config_files(host)
            new_config = config_files[-1] if config_files else None

            # Compare and cleanup
            diff_file = diff_and_cleanup(host)

            # Display diff if changes found
            if diff_file:
                display_diff(diff_file)

                # Git operations if enabled
                if args.git and new_config:
                    git_commit_and_push(host, new_config)

    print("\n" + "=" * 60)
    print("Orchestration complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
