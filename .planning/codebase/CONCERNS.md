# Concerns

## Security
- **API key in .env** — properly gitignored, but hand-rolled parser has no validation
- **No request timeout** — all `requests.*` calls lack `timeout` parameter; could hang indefinitely
- **No rate limiting** — rapid API calls could hit Clockify rate limits

## Code Quality
- **Duplicated .env parser** — same parsing logic in `init_config.py` and `sync_timing_to_clockify.py`
- **Global mutable state** — `ERRORS` list and config constants are module-level; complicates testing and reuse
- **Monolithic main()** — ~200 lines with mixed concerns (I/O, API calls, business logic, reporting)
- **No input validation on CSV values** — trusts all CSV data without sanitization

## Reliability
- **No retry logic** — API failures cause immediate crash (`.raise_for_status()`)
- **No idempotency guarantee** — if script crashes mid-sync, partial entries exist with no way to resume
- **Additive duration bug risk** — re-running on same CSV adds duration to existing entries rather than replacing

## Scalability
- **All clients/projects loaded upfront** — fine for small workspaces, could be slow for large ones
- **Sequential API calls** — no concurrency for task creation or entry sync
- **Most recent CSV only** — no batch processing of multiple files

## Missing Features (based on error patterns in CSV files)
- No dry-run mode to preview what would be synced
- No undo/rollback capability
- No summary report of what was synced (beyond terminal output)
