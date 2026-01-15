import paramiko
import json

# FortiGate connection details
host = "192.168.1.99"
username = "admin"
password = "jpc1234%"

# Connect to the FortiGate via SSH
try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)

    # Open an interactive shell session
    shell = ssh.invoke_shell()

    # Retrieve the hostname using 'get system status'
    shell.send("get system status\n")
    shell.settimeout(5)
    status_output = ""
    while True:
        try:
            data = shell.recv(1024).decode("utf-8")
            if not data:
                break
            status_output += data
            if "--More--" in data:
                shell.send(" ")
        except Exception:
            break

    # Extract the hostname from the system status output
    hostname = "unknown"
    for line in status_output.splitlines():
        if "Hostname:" in line:
            hostname = line.split(":")[1].strip()
            break

    # Retrieve the full configuration
    shell.send("show full-configuration\n")
    config_output = ""
    while True:
        try:
            data = shell.recv(1024).decode("utf-8")
            if not data:
                break
            config_output += data
            if "--More--" in data:
                shell.send(" ")
        except Exception:
            break

    # Close the connection
    ssh.close()

    # Remove any CLI prompts or extra lines from the configuration output
    config_output = config_output.replace("--More--", "").strip()

    # Split the configuration into individual lines
    config_lines = config_output.splitlines()

    # Wrap the hostname and configuration in JSON format
    result = {
        "hostname": hostname,
        "configuration": config_lines
    }
    print(json.dumps(result, indent=4))

except Exception as e:
    # Return the error in JSON format
    error_result = {"error": str(e)}
    print(json.dumps(error_result, indent=4))
