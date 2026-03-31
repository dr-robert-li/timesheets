# Architecture

## Overview
Single-purpose CLI tool: reads Timing app CSV exports and syncs aggregated time entries to Clockify. No web UI, no database, no background processes.

## Flow
```
CSV File → Parse & Validate → Deduplicate → Aggregate by (client, task, date) → Clockify API sync
```

## Script Roles
1. **`init_config.py`** — Interactive setup wizard. Prompts for API key and default project, writes `.env`.
2. **`sync_timing.py`** — Runner/launcher. Validates venv exists, delegates to core script via subprocess.
3. **`timing-clockify/sync_timing_to_clockify.py`** — Core logic. All business rules, API interaction, error handling.

## Key Design Decisions
- **No client/project auto-creation** — Clients and projects must pre-exist in Clockify to prevent misattribution. Entries for unknown clients are skipped and logged.
- **Aggregation before sync** — Multiple CSV rows for the same (client, task, date) are summed into one time entry.
- **Additive updates** — If a time entry already exists for a task+date, the new duration is added to the existing one.
- **Global mutable state** — `ERRORS` list and config (`API_KEY`, `PROJECT_NAME`) are module-level globals in the core script.
- **Hand-rolled .env parser** — Duplicated in both `init_config.py` and the core script (no shared utility).

## Error Strategy
- Errors collected in global list during processing, written to pipe-delimited log file at end
- Four error types: CLIENT_NOT_FOUND, PROJECT_NOT_FOUND, TIMESPAN_FORMAT_NON_EXACT, DUPLICATE_ENTRY
- Script continues processing on non-fatal errors (skips bad entries)
