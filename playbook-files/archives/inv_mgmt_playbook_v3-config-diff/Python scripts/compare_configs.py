import os
import glob
import difflib
from datetime import datetime

CONFIG_DIR = "/inv_mgmt_playbook/running_config"
CHANGES_DIR = "/inv_mgmt_playbook/changes"

os.makedirs(CHANGES_DIR, exist_ok=True)

# Helper: extract host and timestamp from filename
def parse_filename(filename):
    # Example: switch1_2025-05-21_15-30-45.json
    base = os.path.basename(filename)
    if not base.endswith('.json'):
        return None, None
    try:
        host, dt_str = base.rsplit('_', 1)
        dt_str = dt_str.replace('.json', '')
        # dt_str is now '2025-05-21_15-30-45'
        dt = datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
        return host, dt
    except Exception:
        return None, None

# Build a dict: {host: [(datetime, filename), ...]}
host_files = {}
for f in glob.glob(os.path.join(CONFIG_DIR, "*.json")):
    host, dt = parse_filename(f)
    if host and dt:
        host_files.setdefault(host, []).append((dt, f))

for host, files in host_files.items():
    # Sort files by datetime (newest last)
    files.sort()
    if len(files) < 2:
        print(f"Not enough config files to compare for {host}.")
        continue

    prev_dt, prev_config = files[-2]
    new_dt, new_config = files[-1]

    with open(prev_config, "r") as f1, open(new_config, "r") as f2:
        prev_lines = f1.readlines()
        new_lines = f2.readlines()

    if prev_lines != new_lines:
        # Files differ
        ts = new_dt.strftime("%Y-%m-%d_%H-%M-%S")
        change_file = os.path.join(CHANGES_DIR, f"{host}_change_{ts}.txt")
        with open(change_file, "w") as cf:
            cf.write(f"Change detected for {host} at {ts}\n")
            cf.write(f"Config location: {new_config}\n")
            cf.write("-" * 40 + "\n")
            diff = difflib.unified_diff(
                prev_lines, new_lines,
                fromfile=prev_config, tofile=new_config,
                lineterm='', n=3
            )
            for line in diff:
                cf.write(line + "\n")
        print(f"Config updated and change recorded in {change_file}")
    else:
        # No change, delete the new config
        os.remove(new_config)
        print(f"No change detected for {host}. New config discarded: {new_config}")
