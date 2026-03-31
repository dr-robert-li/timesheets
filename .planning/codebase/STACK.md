# Technology Stack

## Language & Runtime
- **Python 3.14** (via local venv)
- No type hints used
- No linting/formatting tools configured

## Dependencies
- **requests >=2.28.0** — HTTP client for Clockify REST API
- Standard library: csv, os, glob, sys, datetime, collections, subprocess

## External Services
- **Clockify REST API v1** (`https://api.clockify.me/api/v1`)
  - Authentication: API key via `X-Api-Key` header
  - Endpoints used: user, clients, projects, tasks, time-entries (CRUD)

## Configuration
- `.env` file (hand-rolled parser, not python-dotenv)
  - `CLOCKIFY_API_KEY` — API authentication
  - `CLOCKIFY_DEFAULT_PROJECT` — target project name in Clockify

## Build & Run
- No build step — pure Python scripts
- `python3 -m venv venv` for isolation
- `pip install -r timing-clockify/requirements.txt`
- Entry point: `python3 sync_timing.py` (delegates to `timing-clockify/sync_timing_to_clockify.py`)

## Data Format
- Input: CSV exports from Timing macOS app
- Required columns: Duration, Project, Title, Start Date, End Date
- Error output: pipe-delimited `.log` files
