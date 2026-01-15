Once inside the Docker Container, you can run the playbook 2 ways.
1. Run manually
2. Run automatically 

But before that, you need to make your shell script executable

# Make shell script executable
```sh
chmod +x /inv_mgmt_playbook/shell_scripts/run_playbook_v3.sh
```

# 1. Run manually
```sh
/inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh
```

# 2. Run automatically
Add to crontab for running the playbook automatically at specific interval
```sh
crontab -e
# Run every 1 minute
*/1 * * * * /inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh

# Run every 5 minute
*/5 * * * * /inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh

# Run once every day at 10:00 AM
0 10 * * * /inv_mgmt_playbook/shell_scripts/run_playbook_v2.sh
```