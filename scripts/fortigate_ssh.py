#!/usr/bin/env python3
"""
FortiGate SSH Configuration Retriever
Retrieves full configuration from FortiGate firewalls via SSH.
Outputs JSON with hostname and configuration lines.
"""

import os
import json
import paramiko

# Get credentials from environment variables
host = os.environ.get("FORTIGATE_HOST", "192.168.1.99")
username = os.environ.get("FORTIGATE_USER", "admin")
password = os.environ.get("FORTIGATE_PASSWORD", "")

if not password:
    print(json.dumps({"error": "FORTIGATE_PASSWORD environment variable not set"}))
    exit(1)


def recv_until_timeout(shell, timeout=5):
    """Receive data from shell until timeout."""
    shell.settimeout(timeout)
    output = ""
    while True:
        try:
            data = shell.recv(1024).decode("utf-8")
            if not data:
                break
            output += data
            if "--More--" in data:
                shell.send(" ")
        except Exception:
            break
    return output


try:
    # Connect to FortiGate via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)

    shell = ssh.invoke_shell()

    # Get hostname from system status
    shell.send("get system status\n")
    status_output = recv_until_timeout(shell)

    hostname = "unknown"
    for line in status_output.splitlines():
        if "Hostname:" in line:
            hostname = line.split(":")[1].strip()
            break

    # Get full configuration
    shell.send("show full-configuration\n")
    config_output = recv_until_timeout(shell, timeout=30)

    ssh.close()

    # Clean up output
    config_output = config_output.replace("--More--", "").strip()
    config_lines = config_output.splitlines()

    result = {
        "hostname": hostname,
        "configuration": config_lines
    }
    print(json.dumps(result, indent=4))

except Exception as e:
    print(json.dumps({"error": str(e)}))
    exit(1)
