import os
from collections import defaultdict

CONFIG_DIR = "/inv_mgmt_playbook/running_config"

def parse_filename(filename):
    """
    Extract host and timestamp string from filename.
    Example: sandbox_2025-05-21_02-44-02.json
    Returns: ('sandbox', '2025-05-21_02-44-02')
    """
    if not filename.endswith('.json'):
        return None, None
    try:
        host, dt_str = filename.split('_', 1)
        dt_str = dt_str.replace('.json', '')
        return host, dt_str
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return None, None

host_files = defaultdict(list)
files = os.listdir(CONFIG_DIR)
for f in files:
    host, dt_str = parse_filename(f)
    if host and dt_str:
        host_files[host].append((dt_str, f))

for host, filelist in host_files.items():
    # Sort by timestamp string (works for YYYY-MM-DD_HH-MM-SS)
    filelist.sort()
    print(f"Host: {host}")
    for dt_str, fname in filelist:
        print(f"  {dt_str} -> {fname}")
