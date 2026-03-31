# Integrations

## Timing App (macOS) — Data Source
- **Direction:** Import (read-only)
- **Format:** CSV export with exact timespan
- **Fields consumed:** Duration (H:MM:SS), Project, Title, Start Date, End Date, Notes, Billing Status
- **Discovery:** Finds most recent CSV by modification time in project root directory

## Clockify API v1 — Data Target
- **Direction:** Export (read + write)
- **Base URL:** `https://api.clockify.me/api/v1`
- **Auth:** API key in `X-Api-Key` header

### API Calls Made
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/user` | GET | Get workspace ID and user ID |
| `/workspaces/{id}/clients` | GET | List all clients |
| `/workspaces/{id}/projects` | GET | List all projects |
| `/workspaces/{id}/projects/{id}/tasks` | GET | List tasks for a project |
| `/workspaces/{id}/projects/{id}/tasks` | POST | Create new task |
| `/workspaces/{id}/user/{id}/time-entries` | GET | Check existing entries (dedup) |
| `/workspaces/{id}/time-entries` | POST | Create time entry |
| `/workspaces/{id}/time-entries/{id}` | PUT | Update time entry (aggregate) |

### Data Mapping
- Timing **Project** → Clockify **Client** (must pre-exist, matched by exact name)
- Timing **Title** → Clockify **Task** (auto-created as `{Client} - {Title}`)
- All entries go under a single configurable Clockify **Project** per client (default: "GTM Engineering")
- Duration aggregated by (client, task, date) before sync
