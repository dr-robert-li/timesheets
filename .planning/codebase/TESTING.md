# Testing

## Current State
- **No tests exist** — no test files, no test framework, no test configuration
- No CI/CD pipeline
- Manual testing only (run script, check Clockify)

## Test Coverage
- 0% — no automated tests

## Testability Assessment
- Core logic is in pure functions (parsers, aggregators) — easily unit-testable
- API interaction functions are tightly coupled to `requests` — would need mocking
- Global state (`ERRORS` list, module-level config) complicates testing
- `main()` is a monolithic function (~200 lines) — hard to test in isolation

## Recommended Test Areas (if tests are added)
1. CSV parsing (`read_timing_csv`) — various formats, edge cases, missing columns
2. Duration parsing (`parse_duration`) — zero, large values, malformed
3. Aggregation (`aggregate_entries`) — grouping correctness
4. Duplicate detection — exact match, near-match
5. API error handling — network failures, 4xx/5xx responses
