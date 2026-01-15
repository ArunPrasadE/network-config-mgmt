#v1
#!/bin/bash
# Define the inventory file and playbook
INVENTORY="/inv_mgmt_playbook/inventory_2.yml"
PLAYBOOK="/inv_mgmt_playbook/show_run_each.yml"
LOG_DIR="/inv_mgmt_playbook/logs"

# Ensure the log directory exists
mkdir -p "$LOG_DIR"

# Dynamically fetch the list of hosts from the inventory
## jq is used to parse JSON output from ansible-inventory
HOSTS=$(/bin/ansible-inventory -i "$INVENTORY" --list | jq -r '
  to_entries[]
  | select(.value.hosts)
  | .value.hosts[]
' | sort -u)

# Get date from Ansible date time
ANSIBLE_DATE=$(date +%Y-%m-%d)


echo "Hosts found: $HOSTS"

# Loop through each host and run the playbook
echo "Running playbook for each host..."
for HOST in $HOSTS; do
    # Run the playbook for the specific host and write output to a host-specific file
    /bin/ansible-playbook "$PLAYBOOK" -i "$INVENTORY" --limit "$HOST" > "$LOG_DIR/${HOST}_${ANSIBLE_DATE}.log" 2>&1
    # Check if the playbook execution was successful
    if [ $? -ne 0 ]; then
        echo "Error executing playbook for $HOST. Check the log file for details."
    else
        echo "Playbook executed successfully for $HOST."
    fi
    # Check if the files are created for each $HOST in the running_config directory
    if [ -f "/inv_mgmt_playbook/running_config/${HOST}_${ANSIBLE_DATE}.json" ]; then
        echo "Running config file created for $HOST."
        echo ${HOST}_${ANSIBLE_DATE}.json
    else
        echo "Running config file not created for $HOST."
    fi
done
