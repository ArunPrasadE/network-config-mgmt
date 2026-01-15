import os
from datetime import datetime

CONFIG_DIR = "/inv_mgmt_playbook/running_config"

def parse_filename(filename):
    if not filename.endswith('.json'):
        return None, None
    try:
        # Split at the first underscore
        host, dt_str = filename.split('_', 1)
        dt_str = dt_str.replace('.json', '')
        return host, dt_str
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None, None

files = os.listdir(CONFIG_DIR)
for f in files:
    host, dt_str = parse_filename(f)
    print(f"File: {f} | Host: {host} | Timestamp: {dt_str}")
