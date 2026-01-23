#!/usr/bin/env python3
"""
Sync Timing app CSV exports to Clockify.

This script:
- Finds the most recent CSV file in the parent directory
- Matches Timing Project with Clockify Client by name (client must exist)
- Creates time entries under the configured default project (must exist)
- Uses Timing Title as Clockify Task name (creates if not found)
- Aggregates duration by date for matching tasks
- Skips entries for non-existent clients and logs errors
"""

import csv
import os
import glob
import sys
import requests
from datetime import datetime, timedelta
from collections import defaultdict


def load_env_file():
    """Load environment variables from .env file in parent directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    env_path = os.path.join(parent_dir, ".env")

    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars


# Load configuration from .env file
ENV_VARS = load_env_file()
API_KEY = ENV_VARS.get("CLOCKIFY_API_KEY", "")
PROJECT_NAME = ENV_VARS.get("CLOCKIFY_DEFAULT_PROJECT", "GTM Engineering")
BASE_URL = "https://api.clockify.me/api/v1"

if not API_KEY:
    print("Error: CLOCKIFY_API_KEY not found in .env file.")
    print("Please run: python3 init_config.py")
    sys.exit(1)

HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
}

# Global list to collect errors during processing
ERRORS = []


def log_error(message, client_name=None, task_name=None, date=None, duration=None, error_type="UNKNOWN", error_sev="ERROR"):
    """Log an error to the global errors list and print warning."""
    error_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_sev": error_sev,
        "error_type": error_type,
        "message": message,
        "client": client_name,
        "task": task_name,
        "date": str(date) if date else None,
        "duration": str(duration) if duration else None
    }
    ERRORS.append(error_entry)
    prefix = "⚠️  WARNING" if error_sev == "WARNING" else "❌ ERROR"
    print(f"  {prefix}: {message}")


def write_error_log(parent_dir, source_file):
    """Write errors to a log file if there are any. One error per line for easy parsing."""
    if not ERRORS:
        return None

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_filename = f"error-{timestamp}.log"
    log_path = os.path.join(parent_dir, log_filename)

    # Get just the filename from the source path
    source_filename = os.path.basename(source_file) if source_file else "unknown"

    with open(log_path, "w", encoding="utf-8") as f:
        # Write header line
        f.write("timestamp|source_file|error_sev|error_type|client|project|task|date|duration|message\n")

        # Write one error per line
        for error in ERRORS:
            line_parts = [
                error.get('timestamp') or '',
                source_filename,
                error.get('error_sev') or 'ERROR',
                error.get('error_type') or 'UNKNOWN',
                error.get('client') or '',
                PROJECT_NAME,
                error.get('task') or '',
                error.get('date') or '',
                error.get('duration') or '',
                (error.get('message') or '').replace('|', '-')  # Escape any pipe characters in message
            ]
            f.write("|".join(line_parts) + "\n")

    return log_path


def get_workspace_id():
    """Get the user's default workspace ID."""
    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    response.raise_for_status()
    user = response.json()
    return user["defaultWorkspace"]


def get_clients(workspace_id):
    """Get all clients in the workspace."""
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/clients",
        headers=HEADERS
    )
    response.raise_for_status()
    return {client["name"]: client["id"] for client in response.json()}


def get_client(workspace_id, name, all_clients=None):
    """
    Get existing client by name. Returns client_id if found, None if not.
    Does NOT create new clients to prevent misassociation.
    """
    if all_clients is None:
        all_clients = get_clients(workspace_id)

    if name in all_clients:
        print(f"  Found existing client: {name}")
        return all_clients[name]

    return None


def get_projects(workspace_id):
    """Get all projects in the workspace."""
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/projects",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()


def get_project_for_client(workspace_id, project_name, client_id, all_projects=None):
    """
    Get existing project by name that is associated with a specific client.
    Returns project dict if found, None if not.
    Does NOT create new projects to prevent misassociation.
    """
    if all_projects is None:
        all_projects = get_projects(workspace_id)

    # Find project with matching name AND client
    for proj in all_projects:
        if proj["name"] == project_name and proj.get("clientId") == client_id:
            return proj

    return None


def get_tasks(workspace_id, project_id):
    """Get all tasks for a project."""
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/projects/{project_id}/tasks",
        headers=HEADERS
    )
    response.raise_for_status()
    return {task["name"]: task["id"] for task in response.json()}


def create_task(workspace_id, project_id, name):
    """Create a new task."""
    response = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/projects/{project_id}/tasks",
        headers=HEADERS,
        json={"name": name}
    )
    response.raise_for_status()
    return response.json()["id"]


def get_or_create_task(workspace_id, project_id, name):
    """Get existing task or create new one."""
    tasks = get_tasks(workspace_id, project_id)
    if name in tasks:
        print(f"    Found existing task: {name}")
        return tasks[name]
    print(f"    Creating new task: {name}")
    return create_task(workspace_id, project_id, name)


def get_time_entries(workspace_id, user_id, start_date, end_date):
    """Get time entries for a date range."""
    # Format dates as ISO 8601
    start_str = start_date.strftime("%Y-%m-%dT00:00:00Z")
    end_str = end_date.strftime("%Y-%m-%dT23:59:59Z")

    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/user/{user_id}/time-entries",
        headers=HEADERS,
        params={
            "start": start_str,
            "end": end_str
        }
    )
    response.raise_for_status()
    return response.json()


def parse_duration(duration_str):
    """Parse HH:MM:SS duration string to timedelta."""
    if not duration_str or duration_str.strip() == "":
        return timedelta(0)
    parts = duration_str.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def duration_to_iso(td):
    """Convert timedelta to ISO 8601 duration format (PTxHxMxS)."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"PT{hours}H{minutes}M{seconds}S"


def parse_date(date_str):
    """Parse DD/M/YYYY date string to datetime."""
    return datetime.strptime(date_str.strip(), "%d/%m/%Y")


def parse_iso_datetime(dt_str):
    """Parse ISO 8601 datetime string with timezone to datetime."""
    # Handle formats like 2026-01-22T20:00:00+10:00
    dt_str = dt_str.strip()
    # Python's fromisoformat handles this format
    return datetime.fromisoformat(dt_str)


def create_time_entry(workspace_id, project_id, task_id, start_time, duration):
    """Create a time entry."""
    end_time = start_time + duration
    payload = {
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "projectId": project_id,
        "taskId": task_id
    }
    response = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/time-entries",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def update_time_entry(workspace_id, entry_id, start_time, end_time, project_id, task_id):
    """Update a time entry with new end time."""
    payload = {
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "projectId": project_id,
        "taskId": task_id
    }
    response = requests.put(
        f"{BASE_URL}/workspaces/{workspace_id}/time-entries/{entry_id}",
        headers=HEADERS,
        json=payload
    )
    response.raise_for_status()
    return response.json()


def find_most_recent_csv(directory):
    """Find the most recently modified CSV file in the directory."""
    csv_pattern = os.path.join(directory, "*.csv")
    csv_files = glob.glob(csv_pattern)

    if not csv_files:
        return None

    # Sort by modification time, most recent first
    csv_files.sort(key=os.path.getmtime, reverse=True)
    return csv_files[0]


def read_timing_csv(filepath):
    """
    Read and parse Timing app CSV export.
    Requires exact timespan format with Start Date and End Date columns.
    Returns (entries, format_error) tuple.
    """
    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        # Check if required columns exist
        fieldnames = reader.fieldnames or []
        has_start_date = "Start Date" in fieldnames
        has_end_date = "End Date" in fieldnames

        if not has_start_date or not has_end_date:
            return None, "TIMESPAN_FORMAT_NON_EXACT: Please make sure that the Timing Report has Timespan selected and the 'Exact' option selected to prevent duplication of tasks."

        for row in reader:
            # Skip empty rows
            if not row.get("Duration") or not row.get("Project"):
                continue

            # Validate Start Date and End Date are present
            if not row.get("Start Date") or not row.get("End Date"):
                continue

            duration = parse_duration(row["Duration"])
            if duration.total_seconds() == 0:
                continue

            start_date = parse_iso_datetime(row["Start Date"])
            end_date = parse_iso_datetime(row["End Date"])

            entries.append({
                "duration": duration,
                "project": row["Project"].strip(),
                "title": row.get("Title", "").strip() or "General",
                "notes": row.get("Notes", "").strip(),
                "billing_status": row.get("Billing Status", "").strip(),
                "start_date": start_date,
                "end_date": end_date,
                "date": start_date.date()  # Extract date for grouping
            })
    return entries, None


def aggregate_entries(entries):
    """
    Aggregate entries by client, task, and date.
    Returns dict: {(client, task, date): total_duration}
    """
    aggregated = defaultdict(timedelta)
    for entry in entries:
        # entry["date"] is already a date object (extracted from start_date)
        key = (entry["project"], entry["title"], entry["date"])
        aggregated[key] += entry["duration"]
    return aggregated


def main():
    global ERRORS
    ERRORS = []  # Reset errors for each run

    # Find the most recent CSV file in parent directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    csv_file = find_most_recent_csv(parent_dir)
    if not csv_file:
        print("No CSV files found in parent directory")
        return

    print(f"Processing: {os.path.basename(csv_file)}")
    print(f"Modified: {datetime.fromtimestamp(os.path.getmtime(csv_file))}")
    print()

    # Read and parse CSV
    entries, format_error = read_timing_csv(csv_file)
    if format_error:
        log_error(format_error, error_type="TIMESPAN_FORMAT_NON_EXACT", error_sev="ERROR")
        print()
        log_path = write_error_log(parent_dir, csv_file)
        if log_path:
            print(f"❌ Error log written to: {log_path}")
        return

    if not entries:
        print("No valid entries found in CSV")
        return

    # Detect duplicates based on Title + Start Date + End Date
    seen_entries = set()
    unique_entries = []
    duplicate_count = 0

    for entry in entries:
        # Create unique key from title + exact start/end times
        entry_key = (
            entry["project"],
            entry["title"],
            entry["start_date"].isoformat(),
            entry["end_date"].isoformat()
        )

        if entry_key in seen_entries:
            # Log duplicate warning
            log_error(
                f"DUPLICATE ENTRY: '{entry['title']}' with same timespan ({entry['start_date']} to {entry['end_date']}) already exists. Skipping.",
                client_name=entry["project"],
                task_name=entry["title"],
                date=entry["date"],
                duration=entry["duration"],
                error_type="DUPLICATE_ENTRY",
                error_sev="WARNING"
            )
            duplicate_count += 1
        else:
            seen_entries.add(entry_key)
            unique_entries.append(entry)

    entries = unique_entries
    if duplicate_count > 0:
        print(f"Skipped {duplicate_count} duplicate entries")

    print(f"Found {len(entries)} time entries")

    # Aggregate by client, task, and date
    aggregated = aggregate_entries(entries)
    print(f"Aggregated to {len(aggregated)} unique client/task/date combinations")
    print()

    # Get workspace and user info
    print("Connecting to Clockify...")
    workspace_id = get_workspace_id()

    response = requests.get(f"{BASE_URL}/user", headers=HEADERS)
    user_id = response.json()["id"]

    print(f"Workspace ID: {workspace_id}")
    print()

    # Get existing clients upfront for validation
    print("Loading existing clients...")
    all_clients = get_clients(workspace_id)
    print(f"  Found {len(all_clients)} clients: {', '.join(all_clients.keys())}")
    print()

    # Get all projects upfront for validation
    print("Loading existing projects...")
    all_projects = get_projects(workspace_id)
    print(f"  Found {len(all_projects)} projects")
    print()

    # Track statistics
    processed_count = 0
    skipped_count = 0

    # Process each aggregated entry
    for (client_name, task_name, entry_date), total_duration in aggregated.items():
        print(f"Processing: {client_name} / {task_name} on {entry_date}")
        print(f"  Total duration: {total_duration}")

        # Check if client exists (do NOT create)
        client_id = get_client(workspace_id, client_name, all_clients)
        if not client_id:
            error_msg = f"CLIENT NOT FOUND: Client '{client_name}' does not exist in Clockify. Skipping entry to prevent misassociation."
            log_error(error_msg, client_name, task_name, entry_date, total_duration, error_type="CLIENT_NOT_FOUND")
            skipped_count += 1
            print()
            continue

        # Check if GTM Engineering project exists for THIS specific client
        project = get_project_for_client(workspace_id, PROJECT_NAME, client_id, all_projects)
        if not project:
            error_msg = f"PROJECT NOT FOUND: Project '{PROJECT_NAME}' does not exist for client '{client_name}'. Skipping entry to prevent misassociation with wrong client."
            log_error(error_msg, client_name, task_name, entry_date, total_duration, error_type="PROJECT_NOT_FOUND")
            print(f"  Found existing client: {client_name}")
            skipped_count += 1
            print()
            continue

        project_id = project["id"]
        print(f"  Found existing client: {client_name}")
        print(f"  Found existing project: {PROJECT_NAME} (for {client_name})")

        # Create task name with client prefix for clarity
        task_full_name = f"{client_name} - {task_name}"

        # Get or create task
        task_id = get_or_create_task(workspace_id, project_id, task_full_name)

        # Check for existing time entries on this date for this task
        entry_datetime = datetime.combine(entry_date, datetime.min.time())
        existing_entries = get_time_entries(
            workspace_id,
            user_id,
            entry_datetime,
            entry_datetime
        )

        # Find existing entry for same project and task
        existing_entry = None
        existing_duration = timedelta(0)
        for entry in existing_entries:
            if entry.get("projectId") == project_id and entry.get("taskId") == task_id:
                existing_entry = entry
                # Calculate existing duration
                start = datetime.fromisoformat(entry["timeInterval"]["start"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(entry["timeInterval"]["end"].replace("Z", "+00:00"))
                existing_duration = end - start
                break

        if existing_entry:
            # Update existing entry by adding duration
            new_duration = existing_duration + total_duration
            start_time = datetime.combine(entry_date, datetime.min.time().replace(hour=9))
            end_time = start_time + new_duration

            print(f"    Updating existing entry: {existing_duration} + {total_duration} = {new_duration}")
            update_time_entry(
                workspace_id,
                existing_entry["id"],
                start_time,
                end_time,
                project_id,
                task_id
            )
        else:
            # Create new time entry
            start_time = datetime.combine(entry_date, datetime.min.time().replace(hour=9))

            print(f"    Creating new entry: {total_duration}")
            create_time_entry(
                workspace_id,
                project_id,
                task_id,
                start_time,
                total_duration
            )

        processed_count += 1
        print()

    # Summary
    print("=" * 50)
    print(f"Sync complete!")
    print(f"  Processed: {processed_count} entries")
    print(f"  Skipped: {skipped_count} entries")

    # Write error log if there were any issues
    if ERRORS:
        log_path = write_error_log(parent_dir, csv_file)
        print()
        print(f"⚠️  {len(ERRORS)} error(s) occurred. See log file:")
        print(f"   {log_path}")


if __name__ == "__main__":
    main()
