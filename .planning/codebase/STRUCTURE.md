# Project Structure

```
timesheets/
├── .env                              # Config (API key, default project) — gitignored
├── .gitignore                        # Broad exclusions (csv, pdf, log, json, office docs, etc.)
├── LICENSE                           # MIT
├── README.md                         # Setup & usage docs
├── init_config.py                    # Interactive config setup (writes .env)
├── sync_timing.py                    # Runner script (launches core via subprocess)
├── venv/                             # Python 3.14 virtual environment — gitignored
├── *.csv                             # Timing app CSV exports (13 files) — gitignored
├── timing-clockify/
│   ├── requirements.txt              # Dependencies (requests>=2.28.0)
│   └── sync_timing_to_clockify.py    # Core sync logic (~560 lines)
└── .planning/                        # GSD planning artifacts
    └── codebase/                     # This codebase map
```

## File Sizes
| File | Lines | Purpose |
|------|-------|---------|
| `sync_timing_to_clockify.py` | 561 | Core logic — CSV parsing, API calls, sync |
| `init_config.py` | 104 | Config wizard |
| `sync_timing.py` | 34 | Runner/launcher |
| `requirements.txt` | 1 | Single dependency |

## Key Patterns
- Core logic isolated in `timing-clockify/` subdirectory
- Runner script in root for convenience (`python3 sync_timing.py`)
- CSV data files live alongside scripts in root (gitignored)
- No package structure (no `__init__.py`, no setup.py/pyproject.toml)
