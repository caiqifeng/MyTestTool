# I18n Image Check Service Design

> This spec defines the new always-on management service for the existing `check_i18n_images.py` workflow. It was discussed and approved before implementation planning.

## Goal

Deploy the image checking system on one machine as a persistent web service that supports:

- Daily scheduled execution.
- Manual execution from a page.
- A current clean report that only reflects the latest valid scan.
- Historical report retention for the latest 5 successful runs.
- Cleanup of obsolete report assets.
- OCR cache lifecycle management for stale MD5 records.

The service must not delete or modify real source image files under `trunk/client` or any configured resource root.

## Scope

### In Scope

- Add an independent management service, tentatively `report_service.py`.
- Keep the existing checking script as the scan/report engine.
- Provide a web console for status, manual run, history, and basic config.
- Run the check automatically once per day at a configured time.
- Prevent concurrent runs.
- Store each run in an isolated report directory.
- Retain the latest 5 successful report runs.
- Keep failed run logs separately for troubleshooting.
- Archive stale OCR MD5 records before deleting them after a retention period.

### Out of Scope

- Deleting source `.dds` or `.tga` files from the client resource tree.
- Automatically committing, reverting, or syncing resource repositories.
- Replacing OCR behavior or changing the core image comparison rules.
- Building a multi-user permission system.
- Deploying to multiple machines.

## Chosen Approach

Use an independent management service.

The service owns scheduling, web UI, run history, and cleanup. It should reuse the existing checking logic from `check_i18n_images.py` where practical. If direct import becomes risky because of global state or long-running service concerns, the implementation may call the script as a subprocess, but the design target is a separate service boundary rather than expanding the main script.

Rationale:

- Keeps `check_i18n_images.py` focused on scanning, OCR, comparison, and report generation.
- Allows service concerns to be tested and evolved independently.
- Provides one operational entry point for scheduled and manual execution.

## Service Configuration

Create `report_service_config.json` in the project root when missing.

Default configuration:

```json
{
  "host": "127.0.0.1",
  "port": 9080,
  "check_config": "check_config.json",
  "daily_run_time": "02:00",
  "history_success_limit": 5,
  "history_failed_limit": 5,
  "ocr_archive_retention_days": 30,
  "reports_dir": "reports"
}
```

Field requirements:

| Field | Meaning |
| --- | --- |
| `host` | Bind host for the management service. Default local-only. |
| `port` | Bind port for the management service. |
| `check_config` | Path to the existing image check config. |
| `daily_run_time` | Daily execution time in `HH:MM` 24-hour local time. |
| `history_success_limit` | Number of successful run directories to retain. Default 5. |
| `history_failed_limit` | Number of failed run logs/directories to retain. Default 5. |
| `ocr_archive_retention_days` | Number of days to keep archived OCR records before physical deletion. Default 30. |
| `reports_dir` | Root directory for service-owned reports and run metadata. |

Invalid config must not start a scan. The service should show the validation error on the console page and in `/api/status`.

## Directory Layout

Service-owned files live under `reports/` by default:

```text
reports/
  runs/
    20260610_020000/
      ui_image_check_report.html
      ui_image_check_report_assets/
      run.log
      metadata.json
  failed/
    20260610_021500/
      run.log
      metadata.json
  index.json
```

`metadata.json` should contain:

- `run_id`
- `trigger`: `manual` or `scheduled`
- `status`: `running`, `success`, `failed`, `skipped`
- `started_at`
- `finished_at`
- `duration_seconds`
- `report_path`
- `log_path`
- `error_summary`
- `counts` if available

`index.json` should contain:

- `latest_success_run_id`
- recent successful runs
- recent failed runs
- service config snapshot relevant to scheduling

The current report is a pointer to `latest_success_run_id`, not a separately edited copy. Failed runs must not replace the latest successful report.

## Run Lifecycle

### 1. Create Run

When a manual or scheduled trigger starts:

- Generate `run_id` as `YYYYMMDD_HHMMSS`.
- Create `reports/runs/<run_id>/`.
- Create `metadata.json` with `status=running`.
- Start writing `run.log`.

If another run is already active:

- Manual trigger returns a conflict response with the active run id.
- Scheduled trigger is skipped and recorded as skipped.

### 2. Execute Check

The run uses the configured `check_config` and outputs:

- `reports/runs/<run_id>/ui_image_check_report.html`
- `reports/runs/<run_id>/ui_image_check_report_assets/`
- `reports/runs/<run_id>/run.log`

The implementation should preserve current check behavior:

- Same image comparison rules.
- Same OCR cache database unless explicitly configured later.
- Same HTML report interaction behavior.

### 3. Publish Latest

On success:

- Mark run metadata `status=success`.
- Update `reports/index.json.latest_success_run_id`.
- Current report page links to this run.
- Run cleanup after publishing.

On failure:

- Mark run metadata `status=failed`.
- Move or register the run under failed history.
- Keep the previous latest successful report unchanged.
- Show the error summary and log link in the console.

### 4. Cleanup Report History

After every run:

- Keep only the latest `history_success_limit` successful runs.
- Keep only the latest `history_failed_limit` failed runs.
- Delete removed run directories entirely, including HTML and asset folders.

This solves stale HTML display assets without touching real source images.

### 5. Cleanup OCR Cache

The current `.ocr_cache.db` behavior keys active cache lookup by `relative_path + md5`. Old records for a changed file become unused when MD5 changes.

New lifecycle:

- Add an archive table, for example `ocr_cache_archive`.
- When a cache entry for `relative_path` is replaced by a different MD5, copy the old record into archive before updating active cache.
- Archive entries include `archived_at`.
- Archive entries are kept for `ocr_archive_retention_days`.
- Entries older than retention are physically deleted.
- Review operations such as `ignore` remain tied to `relative_path + md5`, so a changed file must not inherit the old ignore state.

The service cleanup job should also be callable after a successful scan.

## Web Console

The root page `GET /` is the management console.

Required UI:

- Current service status.
- Active run progress or idle state.
- Last successful run time.
- Next scheduled run time.
- Button: run now.
- Link: open current report.
- Recent successful run list, max 5.
- Recent failed run list, max 5.
- Link to run logs.
- Basic config form for:
  - daily run time
  - success history limit
  - failed history limit
  - OCR archive retention days

UI behavior:

- Disable run button while a run is active.
- Poll `/api/status` while running.
- Do not show stale failed output as the current report.
- Surface config and environment errors in plain language.

## HTTP API

### `GET /api/status`

Returns:

- service status
- active run metadata if any
- latest successful run
- recent failures
- next scheduled run time
- config validation result

### `POST /api/runs`

Starts a manual run.

Responses:

- `202 Accepted` with run metadata if started.
- `409 Conflict` if another run is active.
- `400 Bad Request` if config is invalid.

### `GET /api/runs`

Returns recent successful and failed runs.

### `GET /reports/runs/<run_id>/ui_image_check_report.html`

Serves a retained report.

### `POST /api/ocr-cache/operation`

Preserves the existing report page behavior for ignore operations.

Requirements:

- Writes operation by `relativePath + md5`.
- Must not apply an old operation to a changed MD5.

### `POST /api/config`

Updates editable service settings.

Requirements:

- Validate `daily_run_time` as `HH:MM`.
- Validate retention values as positive integers.
- Save config atomically.
- Recompute next scheduled run immediately.

## Scheduler

The service runs an internal scheduler loop.

Requirements:

- Default run time is `02:00` local machine time.
- The page can change the time.
- If the service is down at the scheduled time, it does not attempt catch-up by default.
- If a run is active at scheduled time, skip this scheduled run and log the skip.
- Scheduler must survive scan failures and continue scheduling future runs.

## Error Handling

| Scenario | Behavior |
| --- | --- |
| Config file missing | Mark run failed, keep latest successful report unchanged. |
| Resource directory missing | Mark run failed and expose generated error report/log. |
| OCR dependency missing | Mark run failed with install guidance from existing checker. |
| Pillow missing | Mark run failed with existing install guidance. |
| Port already in use | Service startup fails with a clear message. |
| Manual run while scheduled run active | Return conflict and show active run. |
| Service restart | Load `reports/index.json` and recover latest/history state. |

## Data Safety

The service may delete:

- old `reports/runs/<run_id>/` directories beyond retention
- old `reports/failed/<run_id>/` directories beyond retention
- expired OCR archive records

The service must not delete:

- source images under `trunk/client`
- configured `i18n` or `mainland` directories
- `.ocr_cache.db` active records for current MD5 values
- user-edited config unless saving an explicit page config change

## Testing Requirements

Add tests for:

- config load, default creation, and validation
- scheduler next-run calculation
- manual run conflict when active
- successful run metadata and latest pointer update
- failed run not replacing latest
- successful history retention at 5
- failed history retention at 5
- report directory cleanup deletes only service-owned directories
- OCR old MD5 archive on replacement
- OCR archive retention deletion
- ignore operation keyed by `relative_path + md5`

## Acceptance Criteria

- Starting the service opens a console page on configured host/port.
- Manual run can be triggered from the page.
- Daily scheduled run executes at the configured time.
- While a run is active, a second run cannot start.
- Latest report always points to the most recent successful run.
- Failed runs are visible but do not replace the current report.
- Only the latest 5 successful report runs are retained by default.
- Report asset directories older than retention are removed with their run directory.
- OCR cache entries for changed MD5 values are archived before replacement.
- OCR archive entries older than 30 days are physically deleted.
- No real source image files are deleted by the service.
