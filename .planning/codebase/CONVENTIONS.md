# Conventions

## Code Style
- Python with no enforced style guide (no linter/formatter configured)
- snake_case for functions and variables
- UPPER_CASE for module-level constants
- Docstrings on all functions (short, descriptive)
- Print statements for user feedback (no logging module)

## Patterns
- Functions are procedural — no classes used
- API calls wrapped in thin functions (one per endpoint)
- All Clockify API functions take `workspace_id` as first param
- Optional `all_*` params to avoid redundant API calls (batch-loaded upfront)
- Error collection via global list with structured dicts

## Configuration
- `.env` file with KEY=VALUE format (no quotes, no interpolation)
- Hand-rolled parser (not python-dotenv) — duplicated in two files
- Module-level globals for config values (`API_KEY`, `PROJECT_NAME`, `HEADERS`)

## Naming
- CSV columns referenced by Timing app names: "Duration", "Project", "Title", "Start Date", "End Date"
- Clockify terminology: workspace, client, project, task, time-entry
- Timing "Project" maps to Clockify "Client" (potentially confusing)
