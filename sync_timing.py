#!/usr/bin/env python3
"""
Runner script for syncing Timing app CSV exports to Clockify.
This script runs the sync_timing_to_clockify.py script from the timing-clockify subfolder.
"""

import subprocess
import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    subfolder = os.path.join(script_dir, "timing-clockify")
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
    sync_script = os.path.join(subfolder, "sync_timing_to_clockify.py")

    # Check if venv exists
    if not os.path.exists(venv_python):
        print(f"Error: Virtual environment not found at {venv_python}")
        print("Please run: python3 -m venv venv && source venv/bin/activate && pip install -r timing-clockify/requirements.txt")
        sys.exit(1)

    # Check if sync script exists
    if not os.path.exists(sync_script):
        print(f"Error: Sync script not found at {sync_script}")
        sys.exit(1)

    # Run the sync script using the venv's Python
    result = subprocess.run([venv_python, sync_script], cwd=script_dir)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
