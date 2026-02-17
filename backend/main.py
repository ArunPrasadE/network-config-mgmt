#!/usr/bin/env python3
"""
Network Configuration Management - FastAPI Backend

Provides REST API for:
- Host management (list, add, get groups)
- Configuration collection (run playbooks)
- Config/diff/log file retrieval
"""

import os
import re
import json
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yaml

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
PLAYBOOKS_DIR = PROJECT_ROOT / "playbooks"
INVENTORY_FILE = PLAYBOOKS_DIR / "inventory.yml"
HOST_VARS_DIR = PLAYBOOKS_DIR / "host_vars"
CONFIG_DIR = PROJECT_ROOT / "output" / "configs"
CHANGES_DIR = PROJECT_ROOT / "output" / "changes"
LOG_DIR = PROJECT_ROOT / "output" / "logs"
ORCHESTRATOR = PROJECT_ROOT / "scripts" / "orchestrator.py"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CHANGES_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Network Config Management API",
    description="API for managing network device configurations",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track running jobs
running_jobs = {}


class HostCreate(BaseModel):
    hostname: str
    group: str
    ansible_host: str
    ansible_connection: Optional[str] = None
    ansible_network_os: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    hostname: str
    status: str  # "running", "completed", "failed"
    started_at: str
    completed_at: Optional[str] = None
    log_file: Optional[str] = None
    error: Optional[str] = None


# ============== Host Management ==============

@app.get("/api/hosts")
async def list_hosts():
    """Get all hosts from inventory."""
    try:
        result = subprocess.run(
            ["ansible-inventory", "-i", str(INVENTORY_FILE), "--list"],
            capture_output=True,
            text=True,
            check=True
        )
        inventory = json.loads(result.stdout)

        hosts = []
        host_meta = inventory.get("_meta", {}).get("hostvars", {})

        # Map hosts to their groups
        group_map = {}
        for group_name, group_data in inventory.items():
            if group_name.startswith("_"):
                continue
            if isinstance(group_data, dict) and "hosts" in group_data:
                for host in group_data["hosts"]:
                    group_map[host] = group_name

        for hostname in sorted(group_map.keys()):
            host_vars = host_meta.get(hostname, {})
            hosts.append({
                "hostname": hostname,
                "group": group_map.get(hostname, "unknown"),
                "ansible_host": host_vars.get("ansible_host", hostname),
                "ansible_connection": host_vars.get("ansible_connection", ""),
                "ansible_network_os": host_vars.get("ansible_network_os", "")
            })

        return {"hosts": hosts}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error reading inventory: {e.stderr}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing inventory: {str(e)}")


@app.get("/api/groups")
async def list_groups():
    """Get available device groups."""
    groups = [
        {"name": "nxos", "description": "Cisco NX-OS switches"},
        {"name": "ios", "description": "Cisco IOS switches"},
        {"name": "vswitch", "description": "Cisco NX-OS virtual switches"},
        {"name": "cumulus", "description": "Cumulus Linux switches"},
        {"name": "fortigate", "description": "FortiGate firewalls"}
    ]
    return {"groups": groups}


@app.post("/api/hosts")
async def add_host(host: HostCreate):
    """Add a new host to inventory and create host_vars file."""
    try:
        # Read current inventory
        with open(INVENTORY_FILE, 'r') as f:
            inventory = yaml.safe_load(f)

        # Check if host already exists
        for group_name, group_data in inventory.get("all", {}).get("children", {}).items():
            if isinstance(group_data, dict) and "hosts" in group_data:
                if group_data["hosts"] and host.hostname in group_data["hosts"]:
                    raise HTTPException(status_code=400, detail=f"Host '{host.hostname}' already exists")

        # Add host to the appropriate group
        children = inventory.get("all", {}).get("children", {})
        if host.group not in children:
            raise HTTPException(status_code=400, detail=f"Unknown group: {host.group}")

        group_data = children[host.group]
        if "hosts" not in group_data or group_data["hosts"] is None:
            group_data["hosts"] = {}

        group_data["hosts"][host.hostname] = None

        # Write updated inventory
        with open(INVENTORY_FILE, 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, sort_keys=False)

        # Create host_vars file
        host_vars = {"ansible_host": host.ansible_host}
        if host.ansible_connection:
            host_vars["ansible_connection"] = host.ansible_connection
        if host.ansible_network_os:
            host_vars["ansible_network_os"] = host.ansible_network_os

        host_vars_file = HOST_VARS_DIR / f"{host.hostname}.yml"
        with open(host_vars_file, 'w') as f:
            yaml.dump(host_vars, f, default_flow_style=False)

        return {"message": f"Host '{host.hostname}' added successfully", "hostname": host.hostname}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Config Collection ==============

async def run_orchestrator_async(hostname: str, job_id: str):
    """Run orchestrator in background."""
    try:
        running_jobs[job_id]["status"] = "running"

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = LOG_DIR / f"job_{hostname}_{timestamp}.log"

        running_jobs[job_id]["log_file"] = str(log_file)

        # Run orchestrator
        process = await asyncio.create_subprocess_exec(
            "python3", str(ORCHESTRATOR), "--host", hostname,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(PROJECT_ROOT)
        )

        stdout, _ = await process.communicate()

        # Write log
        with open(log_file, 'w') as f:
            f.write(stdout.decode())

        if process.returncode == 0:
            running_jobs[job_id]["status"] = "completed"
        else:
            running_jobs[job_id]["status"] = "failed"
            running_jobs[job_id]["error"] = f"Process exited with code {process.returncode}"

        running_jobs[job_id]["completed_at"] = datetime.now().isoformat()

    except Exception as e:
        running_jobs[job_id]["status"] = "failed"
        running_jobs[job_id]["error"] = str(e)
        running_jobs[job_id]["completed_at"] = datetime.now().isoformat()


@app.post("/api/run/{hostname}")
async def run_config_collection(hostname: str, background_tasks: BackgroundTasks):
    """Trigger configuration collection for a host."""
    # Verify host exists
    hosts_response = await list_hosts()
    host_exists = any(h["hostname"] == hostname for h in hosts_response["hosts"])

    if not host_exists:
        raise HTTPException(status_code=404, detail=f"Host '{hostname}' not found")

    # Check if already running
    for job_id, job in running_jobs.items():
        if job["hostname"] == hostname and job["status"] == "running":
            return {"job_id": job_id, "message": "Job already running", "status": "running"}

    # Create new job
    job_id = f"{hostname}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    running_jobs[job_id] = {
        "job_id": job_id,
        "hostname": hostname,
        "status": "pending",
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "log_file": None,
        "error": None
    }

    # Start background task
    background_tasks.add_task(run_orchestrator_async, hostname, job_id)

    return {"job_id": job_id, "message": "Job started", "status": "pending"}


@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a running job."""
    if job_id not in running_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return running_jobs[job_id]


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return {"jobs": list(running_jobs.values())}


# ============== Config/Diff/Log Retrieval ==============

@app.get("/api/configs/{hostname}")
async def get_host_configs(hostname: str):
    """Get all configuration files for a host."""
    pattern = f"{hostname}_*.json"
    files = sorted(CONFIG_DIR.glob(pattern), reverse=True)

    configs = []
    for f in files:
        # Extract timestamp from filename
        match = re.search(r'_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.json$', f.name)
        timestamp = match.group(1) if match else "unknown"

        configs.append({
            "filename": f.name,
            "timestamp": timestamp,
            "size": f.stat().st_size,
            "path": str(f)
        })

    return {"hostname": hostname, "configs": configs}


@app.get("/api/configs/{hostname}/latest")
async def get_latest_config(hostname: str):
    """Get the latest configuration for a host."""
    pattern = f"{hostname}_*.json"
    files = sorted(CONFIG_DIR.glob(pattern))

    if not files:
        raise HTTPException(status_code=404, detail=f"No configs found for {hostname}")

    latest = files[-1]
    content = latest.read_text()

    # Parse sections from the config content
    sections = parse_config_sections(content)

    return {
        "hostname": hostname,
        "filename": latest.name,
        "timestamp": re.search(r'_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.json$', latest.name).group(1),
        "content": content,
        "sections": sections
    }


def parse_config_sections(content: str) -> List[dict]:
    """Parse config content into sections based on === headers."""
    sections = []
    current_section = None
    current_content = []

    for line in content.split('\n'):
        if line.startswith('===') and '===' in line[3:]:
            # Save previous section
            if current_section:
                sections.append({
                    "title": current_section,
                    "content": '\n'.join(current_content).strip()
                })
            # Start new section
            current_section = line.strip('= \n')
            current_content = []
        else:
            current_content.append(line)

    # Save last section
    if current_section:
        sections.append({
            "title": current_section,
            "content": '\n'.join(current_content).strip()
        })

    return sections


@app.get("/api/changes/{hostname}")
async def get_host_changes(hostname: str):
    """Get all change/diff files for a host."""
    pattern = f"{hostname}_change_*.diff"
    files = sorted(CHANGES_DIR.glob(pattern), reverse=True)

    changes = []
    for f in files:
        match = re.search(r'_change_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.diff$', f.name)
        timestamp = match.group(1) if match else "unknown"

        changes.append({
            "filename": f.name,
            "timestamp": timestamp,
            "size": f.stat().st_size,
            "path": str(f)
        })

    return {"hostname": hostname, "changes": changes}


@app.get("/api/changes/{hostname}/latest")
async def get_latest_change(hostname: str):
    """Get the latest change diff for a host."""
    pattern = f"{hostname}_change_*.diff"
    files = sorted(CHANGES_DIR.glob(pattern))

    if not files:
        return {"hostname": hostname, "has_changes": False, "message": "No changes detected"}

    latest = files[-1]
    content = latest.read_text()

    # Parse diff into structured format
    diff_data = parse_diff(content)

    return {
        "hostname": hostname,
        "has_changes": True,
        "filename": latest.name,
        "timestamp": re.search(r'_change_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.diff$', latest.name).group(1),
        "content": content,
        "diff": diff_data
    }


def parse_diff(content: str) -> dict:
    """Parse diff content into additions and removals."""
    additions = []
    removals = []

    for line in content.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            additions.append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removals.append(line[1:])

    return {
        "additions": additions,
        "removals": removals,
        "additions_count": len(additions),
        "removals_count": len(removals)
    }


@app.get("/api/logs/{hostname}")
async def get_host_logs(hostname: str):
    """Get all log files for a host."""
    # Match both orchestrator logs and job logs
    patterns = [f"{hostname}_*.log", f"job_{hostname}_*.log"]

    files = []
    for pattern in patterns:
        files.extend(LOG_DIR.glob(pattern))

    files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)

    logs = []
    for f in files:
        logs.append({
            "filename": f.name,
            "timestamp": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": f.stat().st_size,
            "path": str(f)
        })

    return {"hostname": hostname, "logs": logs}


@app.get("/api/logs/{hostname}/latest")
async def get_latest_log(hostname: str):
    """Get the latest log file content for a host."""
    patterns = [f"{hostname}_*.log", f"job_{hostname}_*.log"]

    files = []
    for pattern in patterns:
        files.extend(LOG_DIR.glob(pattern))

    if not files:
        raise HTTPException(status_code=404, detail=f"No logs found for {hostname}")

    latest = sorted(files, key=lambda x: x.stat().st_mtime)[-1]
    content = latest.read_text()

    # Extract errors from log
    errors = extract_errors(content)

    return {
        "hostname": hostname,
        "filename": latest.name,
        "path": str(latest),
        "content": content,
        "errors": errors,
        "has_errors": len(errors) > 0
    }


def extract_errors(content: str) -> List[str]:
    """Extract error lines from log content."""
    error_patterns = [
        r'.*\[ERROR\].*',
        r'.*error:.*',
        r'.*Error:.*',
        r'.*FAILED.*',
        r'.*fatal:.*',
        r'.*unreachable.*'
    ]

    errors = []
    for line in content.split('\n'):
        for pattern in error_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                errors.append(line.strip())
                break

    return errors


# ============== Dashboard Summary ==============

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get summary data for dashboard."""
    hosts_response = await list_hosts()
    hosts = hosts_response["hosts"]

    summary = {
        "total_hosts": len(hosts),
        "hosts_by_group": {},
        "recent_changes": [],
        "total_configs": 0,
        "total_changes": 0
    }

    # Count hosts by group
    for host in hosts:
        group = host["group"]
        summary["hosts_by_group"][group] = summary["hosts_by_group"].get(group, 0) + 1

    # Count total configs
    summary["total_configs"] = len(list(CONFIG_DIR.glob("*.json")))

    # Count total changes
    summary["total_changes"] = len(list(CHANGES_DIR.glob("*.diff")))

    # Get recent changes (last 10)
    change_files = sorted(CHANGES_DIR.glob("*.diff"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
    for f in change_files:
        match = re.match(r'(.+)_change_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})\.diff$', f.name)
        if match:
            summary["recent_changes"].append({
                "hostname": match.group(1),
                "timestamp": match.group(2),
                "filename": f.name
            })

    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
