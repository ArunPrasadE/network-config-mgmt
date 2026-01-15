#!/bin/bash

# Define the inventory file and playbook
INVENTORY="/inv_mgmt_playbook/inventory_2.yml"
PLAYBOOK="/inv_mgmt_playbook/show_run_each.yml"
LOG_DIR="/inv_mgmt_playbook/logs"
CONFIG_DIR="/inv_mgmt_playbook/running_config"
CHANGES_DIR="/inv_mgmt_playbook/changes"
GIT_PUSH_DIR="/inv_mgmt_playbook/git_push"  # New directory for Git uploads

# Ensure the log, changes, and git_push directories exist
mkdir -p "$LOG_DIR"
mkdir -p "$CHANGES_DIR"
mkdir -p "$GIT_PUSH_DIR"  # Create the git_push directory


# Function to compare configs, ignore time lines, and manage diffs
diff_and_cleanup() {
    local HOST="$1"
    local IGNORE_PATTERNS='^!Time:|^!Running configuration last done at:'

    # Find the two most recent config files for this host
    local files=($(ls "$CONFIG_DIR"/${HOST}_*.json 2>/dev/null | sort))
    local num_files=${#files[@]}

    echo "Host: "
    echo "========================="
    echo "$HOST"
    echo

    if [ "$num_files" -lt 2 ]; then
        echo "  !!! Not enough files to compare !!!"
        echo
        return
    fi

    local prev_file="${files[$num_files-2]}"
    local new_file="${files[$num_files-1]}"

    echo "  Previous: $(basename "$prev_file")"
    echo
    echo "  New:      $(basename "$new_file")"
    echo

    # Filter out ignored lines and compare
    local prev_tmp=$(mktemp)
    local new_tmp=$(mktemp)
    grep -Ev "$IGNORE_PATTERNS" "$prev_file" > "$prev_tmp"
    grep -Ev "$IGNORE_PATTERNS" "$new_file" > "$new_tmp"

    if ! diff -q "$prev_tmp" "$new_tmp" >/dev/null; then
        echo " !!! Files are DIFFERENT! Writing diff report and updating baseline !!!"
        echo

        local diff_file="$CHANGES_DIR/${HOST}_change_$(basename "$new_file" .json).diff"
        echo "### Diff for $HOST at $(basename "$new_file" .json):" > "$diff_file ###"
        diff -u "$prev_tmp" "$new_tmp" >> "$diff_file"
        echo 
        echo " ### Diff written to: $diff_file ###"
        echo

        local git_upload_file="$GIT_PUSH_DIR/${HOST}_running_config.json"  # Only hostname for git upload

        # Replace the old file, keep the new one as the new baseline
        cp "$new_file" "$git_upload_file"  # Copy to git_push directory

        echo " ### Updated Git upload file written to: $git_upload_file ###"
        echo

        # Git commands to add, commit, and push the updated file
        cd "$GIT_PUSH_DIR" || exit  # Change to the git_push directory
        git add "${HOST}_running_config.json"  # Stage the updated file
        git commit -m "[Automatic update] Host: $HOST | $(date)"  # Commit the changes
        git push -u origin HEAD:master  # Push to the remote repository (change 'main' if your branch is different)
        echo " ### Git push completed for $HOST ###"
        echo
        echo "Commit Message: [Automatic update] Host: $HOST | $(date)"
        echo
        

        # Remove the old file, keep the new one as the new baseline
        rm -f "$prev_file"
        echo " !!! Old file deleted: $(basename "$prev_file") !!!"
        echo

    else
        echo " !!! Files are IDENTICAL (ignoring time lines). Deleting new file. !!!"
        echo
        rm -f "$new_file"
        echo " !!! Deleted: $(basename "$new_file") !!!"
        echo
    fi

    rm -f "$prev_tmp" "$new_tmp"
}

# Dynamically fetch the list of hosts from the inventory
HOSTS=$(/bin/ansible-inventory -i "$INVENTORY" --list | jq -r '
  to_entries[]
  | select(.value.hosts)
  | .value.hosts[]
' | sort -u)

# Get date and time for filenames
ANSIBLE_DATE=$(date +%Y-%m-%d)
ANSIBLE_DATE_TIME=$(date +%Y-%m-%d_%H-%M-%S)

echo "Hosts found:"
echo "========================="
echo
echo "$HOSTS"
echo
echo "### Running playbook for each host... ###"
echo

for HOST in $HOSTS; do
    # Run the playbook for the specific host and write output to a host-specific file
    /bin/ansible-playbook "$PLAYBOOK" -i "$INVENTORY" --limit "$HOST" > "$LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log" 2>&1

    # Check if the playbook execution was successful
    if [ $? -ne 0 ]; then
        echo
        echo "!!! Error executing playbook for $HOST. Check the log file for details. !!!"
        echo
    else
        echo
        echo "### Playbook executed successfully for $HOST. ###"
        echo
    fi

    # Check if the config file was created for this host
    if [ -f "$CONFIG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.json" ]; then
        echo
        echo "### Running config file created for $HOST. ###"
        echo "================================================"
        echo
        echo "${HOST}_${ANSIBLE_DATE_TIME}.json"
        echo
        echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"
        echo
    else
        echo
        echo "!!! Running config file not created for $HOST. !!!"
        echo
        echo "Log file: $LOG_DIR/${HOST}_${ANSIBLE_DATE_TIME}.log"
        echo
    fi

    # Run the diff and cleanup function
    echo
    echo "Running diff and cleanup script..."
    echo
    diff_and_cleanup "$HOST"

    # After diff_and_cleanup "$HOST"
    LATEST_DIFF=$(ls -t "$CHANGES_DIR"/${HOST}_change_*.diff 2>/dev/null | head -n1)

    # Check if the diff file was created and is recent 2 minutes
    if [ -n "$LATEST_DIFF" ] && [ "$(stat -c %Y "$LATEST_DIFF")" -ge $(( $(date +%s) - 120 )) ]; then
        echo
        echo "Diff file created: $(basename "$LATEST_DIFF")"
        echo
        echo "Diff results:"
        batcat "$LATEST_DIFF"
        echo
    else
        echo
        echo "Diff file not created."
        echo
    fi
done
