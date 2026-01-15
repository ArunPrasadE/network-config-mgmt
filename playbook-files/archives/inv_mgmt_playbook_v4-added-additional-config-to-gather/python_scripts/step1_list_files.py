import os

CONFIG_DIR = "/inv_mgmt_playbook/running_config"

files = os.listdir(CONFIG_DIR)
print("Files in running_config directory:")
for f in files:
    print(f)