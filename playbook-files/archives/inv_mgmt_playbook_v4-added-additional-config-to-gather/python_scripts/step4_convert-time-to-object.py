import os
from datetime import datetime
from collections import defaultdict

CONFIG_DIR = "/inv_mgmt_playbook/running_config"

def parse_filename(filename):
    """
    Extract host and datetime object from filename.
    Example: sandbox_2025-05-21_02-44-02.json
    Returns: ('sandbox', datetime_object, filename)
    """
    if not filename.endswith('.json'):
        return None, None, None
    try:
        host, dt_str = filename.split('_', 1)
        dt_str = dt_str.replace('.json', '')
        dt = datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
        return host, dt, filename
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None, None, None

host_files = defaultdict(list)
files = os.listdir(CONFIG_DIR)
for f in files:
    host, dt, fname = parse_filename(f)
    if host and dt:
        host_files[host].append((dt, fname))

for host, filelist in host_files.items():
    # Sort by datetime object
    filelist.sort()
    print(f"Host: {host}")
    for dt, fname in filelist:
        print(f"  {dt} -> {fname}")
