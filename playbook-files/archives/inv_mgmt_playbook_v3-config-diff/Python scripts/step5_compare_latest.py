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
    filelist.sort()
    print(f"Host: {host}")
    if len(filelist) < 2:
        print("  Not enough files to compare.")
        continue
    prev_dt, prev_fname = filelist[-2]
    new_dt, new_fname = filelist[-1]
    print(f"  Previous: {prev_fname}")
    print(f"  New:      {new_fname}")
    # Read file contents
    with open(os.path.join(CONFIG_DIR, prev_fname)) as f1, open(os.path.join(CONFIG_DIR, new_fname)) as f2:
        prev_lines = f1.readlines()
        new_lines = f2.readlines()
    if prev_lines != new_lines:
        print("  Files are DIFFERENT!")
    else:
        print("  Files are IDENTICAL.")
