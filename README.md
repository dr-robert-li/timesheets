# Timing to Clockify Sync

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sync time entries from the Timing app (macOS) to Clockify.

## Features

- Reads CSV exports from Timing app
- Matches Timing Project with Clockify Client by name
- Creates time entries under a Clockify configurable default project (e.g., "Engineering from Timing")
- Uses Timing Title as Clockify Task name (creates if not found)
- Aggregates duration by date for matching tasks
- Detects and skips duplicate entries (same Title + Start Date + End Date)
- Validates client and project exist before syncing to prevent misattribution
- Generates error logs for any issues

## Setup

From the `timesheets` directory, run the following commands:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r timing-clockify/requirements.txt
```

### 3. Configure

```bash
python3 init_config.py
```

This will:
- Prompt for your Clockify API key (find it at https://app.clockify.me/user/preferences#advanced)
- Set the default Clockify project for time entries
- Save configuration to `.env` file

## Usage

### 1. Export from Timing

1. Open Timing app
2. Go to Reports
3. Select all available Columns and the date range and projects to export
4. Export as CSV with **Timespan: Exact** selected (required)
5. Save the CSV file to the `timesheets` directory

### 2. Run Sync

```bash
python3 sync_timing.py
```

The script will:
- Find the most recent CSV file in the timesheets directory
- Process and sync entries to Clockify
- Show progress and any errors in the terminal
- Create an error log file if any issues occur

## CSV Format Requirements

The CSV must include these columns:
- `Duration` - Time duration (H:MM:SS)
- `Project` - Must match a Clockify Client name
- `Title` - Used as the Clockify Task name
- `Start Date` - ISO 8601 format with timezone (e.g., 2026-01-22T20:00:00+10:00)
- `End Date` - ISO 8601 format with timezone

**Important:** When exporting from Timing, select "Exact" for Timespan to include Start Date and End Date columns.

## Error Handling

### Error Types

| Error Type | Severity | Description |
|------------|----------|-------------|
| `CLIENT_NOT_FOUND` | ERROR | Timing Project doesn't match any Clockify Client |
| `PROJECT_NOT_FOUND` | ERROR | Default project not found for the matched client |
| `TIMESPAN_FORMAT_NON_EXACT` | ERROR | CSV missing Start Date/End Date columns |
| `DUPLICATE_ENTRY` | WARNING | Entry with same Title + timespan already in file |

### Error Log Format

Errors are logged to `error-{timestamp}.log` in pipe-delimited format:
```
timestamp|source_file|error_sev|error_type|client|project|task|date|duration|message
```

## File Structure

```
timesheets/
├── .env                    # Configuration (API key, default project)
├── .gitignore              # Ignores CSV, PDF, log, and .env files
├── LICENSE                 # MIT License
├── README.md               # This file
├── init_config.py          # Configuration setup script
├── sync_timing.py          # Main runner script
├── venv/                   # Python virtual environment
├── *.csv                   # Timing CSV exports (ignored by git)
├── error-*.log             # Error logs (ignored by git)
└── timing-clockify/
    ├── requirements.txt            # Python dependencies
    └── sync_timing_to_clockify.py  # Core sync logic
```

## Clockify Requirements

Before syncing, ensure in Clockify:
1. **Clients exist** - Create clients matching your Timing Project names
2. **Projects exist** - Create the default project (e.g., "Engineering from Timing") for each client you want to sync - this project will always be the same.

## Troubleshooting

### "CLOCKIFY_API_KEY not found"
Run `python3 init_config.py` to set up your API key.

### "CLIENT_NOT_FOUND" errors
Create a client in Clockify with the exact same name as your Timing Project.

### "PROJECT_NOT_FOUND" errors
Create the default project (check your `.env` file for `CLOCKIFY_DEFAULT_PROJECT`) under the relevant client in Clockify.

### "TIMESPAN_FORMAT_NON_EXACT" error
Re-export from Timing with Timespan set to "Exact" to include Start Date and End Date columns.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
