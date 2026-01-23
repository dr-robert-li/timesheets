#!/bin/bash
# Run the Timing to Clockify sync script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment and run
source venv/bin/activate
python3 sync_timing_to_clockify.py
