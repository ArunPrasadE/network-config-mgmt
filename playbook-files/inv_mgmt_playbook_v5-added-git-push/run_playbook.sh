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
ANSIBLE_DATE_TIME=$(date +%Y-%m-%d_%H-%M-%S)



echo "Hosts found:"
echo
echo "$HOSTS"

# Loop through each host and run the playbook
echo
echo "Running playbook for each host..."
for HOST in $HOSTS; do
    # Run the playbook for the specific host and write output to a host-specific file
    /bin/ansible-playbook "$PLAYBOOK" -i "$INVENTORY" --limit "$HOST" > "$LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log" 2>&1
    # Check if the playbook execution was successful
    if [ $? -ne 0 ]; then
        echo
        echo "Error executing playbook for $HOST. Check the log file for details."
    else
        echo
        echo "Playbook executed successfully for $HOST."
    fi
    # Check if the files are created for each $HOST in the running_config directory
    if [ -f "/inv_mgmt_playbook/running_config/${HOST}_${ANSIBLE_DATE_TIME}.json" ]; then
        echo
        echo "Running config file created for $HOST."
        echo
        echo ${HOST}_${ANSIBLE_DATE_TIME}.json
        echo
        echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"
    else
        echo
        echo "Running config file not created for $HOST."
        echo
        echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"

    fi
    # Run the diff and cleanup script
    echo
    echo "Running diff and cleanup script..."
    python3 /inv_mgmt_playbook/step6_diff_and_cleanup.py

    # Check if the diff and cleanup script executed successfully
    if [ $? -ne 0 ]; then
        echo
        echo "Error executing diff and cleanup script. Check the log file for details."
    else
        echo
        echo "Diff and cleanup script executed successfully."
    fi
    # Check if the diff file was created
    if [ -f "/inv_mgmt_playbook/changes/${HOST}_${ANSIBLE_DATE_TIME}.diff" ]; then
        echo
        echo "Diff file created: ${HOST}_${ANSIBLE_DATE_TIME}.diff"
    else
        echo
        echo "Diff file not created."
    fi
    # Display the diff results
    echo
    echo "Diff results:"
    batcat /inv_mgmt_playbook/changes/${HOST}_${ANSIBLE_DATE_TIME}.diff
done


