import os
from datetime import datetime
from collections import defaultdict
import difflib
import re

CONFIG_DIR = "/inv_mgmt_playbook/running_config"
CHANGES_DIR = "/inv_mgmt_playbook/changes"

os.makedirs(CHANGES_DIR, exist_ok=True)

IGNORE_PATTERNS = [
    r'^!Time:',
    r'^!Running configuration last done at:',
]

def should_ignore(line):
    return any(re.match(pattern, line.strip()) for pattern in IGNORE_PATTERNS)

def parse_filename(filename):
    if not filename.endswith('.json'):
        return None, None, None
    try:
        host, dt_str = filename.split('_', 1)
        dt_str = dt_str.replace('.json', '')
        dt = datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
        return host, dt, filename
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        print()
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
    print()
    if len(filelist) < 2:
        print("  Not enough files to compare.")
        print()
        continue
    prev_dt, prev_fname = filelist[-2]
    new_dt, new_fname = filelist[-1]
    print(f"  Previous: {prev_fname}")
    print()
    print(f"  New:      {new_fname}")
    print()

    # Read and filter file contents
    with open(os.path.join(CONFIG_DIR, prev_fname)) as f1, open(os.path.join(CONFIG_DIR, new_fname)) as f2:
        prev_lines = [line for line in f1 if not should_ignore(line)]
        new_lines = [line for line in f2 if not should_ignore(line)]

    if prev_lines != new_lines:
        print("  Files are DIFFERENT! Writing diff report and updating baseline.")
        print()
        diff = difflib.unified_diff(
            prev_lines, new_lines,
            fromfile=prev_fname, tofile=new_fname,
            lineterm=''
        )
        diff_filename = f"{host}_change_{new_dt.strftime('%Y-%m-%d_%H-%M-%S')}.diff"
        diff_path = os.path.join(CHANGES_DIR, diff_filename)
        with open(diff_path, 'w') as df:
            df.write(f"Diff for {host} at {new_dt}:\n")
            for line in diff:
                df.write(line + '\n')
        print(f"  Diff written to: {diff_path}")
        print()
        # Remove the old file, keep the new one as the new baseline
        os.remove(os.path.join(CONFIG_DIR, prev_fname))
        print(f"  Old file deleted: {prev_fname}")
        print()
    else:
        print("  Files are IDENTICAL (ignoring time lines). Deleting new file.")
        print()
        os.remove(os.path.join(CONFIG_DIR, new_fname))
        print(f"  Deleted: {new_fname}")
        print()
