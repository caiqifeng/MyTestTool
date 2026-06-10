from __future__ import annotations

import json
import mimetypes
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

import check_i18n_images

from .config import save_config, validate_config
from .history import load_index
from .models import ServiceConfig
from .runner import ReportRunner


def status_payload(
    config: ServiceConfig,
    active_run_id: str | None,
    next_run_text: str | None,
    config_errors: list[str] | None = None,
) -> dict[str, object]:
    index = load_index(Path(config.reports_dir))
    return {
        "status": "running" if active_run_id else "idle",
        "active_run_id": active_run_id,
        "next_scheduled_run": next_run_text,
        "latest_success_run_id": index.get("latest_success_run_id"),
        "successful_runs": index.get("successful_runs", []),
        "failed_runs": index.get("failed_runs", []),
        "config": config.to_dict(),
        "config_errors": config_errors or validate_config(config),
    }


def build_console_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>I18n Image Check Service</title>
<style>
body { font-family: Arial, sans-serif; margin: 24px; background: #f6f7f9; color: #20242a; }
main { max-width: 1040px; margin: 0 auto; }
section { background: white; border: 1px solid #d9dee7; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
button { padding: 8px 12px; cursor: pointer; }
button:disabled { opacity: .55; cursor: not-allowed; }
label { display: block; margin: 8px 0; }
input { padding: 6px; }
pre { white-space: pre-wrap; background: #f1f3f6; padding: 12px; }
table { border-collapse: collapse; width: 100%; }
td, th { border-bottom: 1px solid #e1e5ec; padding: 8px; text-align: left; }
</style>
</head>
<body>
<main>
<h1>I18n Image Check Service</h1>
<section>
  <h2>Status</h2>
  <p id="statusText">Loading...</p>
  <p id="nextRun"></p>
  <button id="runNow" onclick="runNow()">Run Now</button>
  <p><a id="currentReport" href="#" style="display:none">Open Current Report</a></p>
</section>
<section>
  <h2>Config</h2>
  <label>Daily run time <input id="daily_run_time" name="daily_run_time" value="02:00"></label>
  <label>Success history limit <input id="history_success_limit" name="history_success_limit" type="number" value="5"></label>
  <label>Failed history limit <input id="history_failed_limit" name="history_failed_limit" type="number" value="5"></label>
  <label>OCR archive retention days <input id="ocr_archive_retention_days" name="ocr_archive_retention_days" type="number" value="30"></label>
  <button onclick="saveConfig()">Save Config</button>
</section>
<section>
  <h2>Runs</h2>
  <table>
    <thead><tr><th>Run</th><th>Status</th><th>Trigger</th><th>Started</th><th>Report</th></tr></thead>
    <tbody id="runs"></tbody>
  </table>
</section>
<section>
  <h2>Raw Status</h2>
  <pre id="rawStatus"></pre>
</section>
</main>
<script>
async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || (data.errors || []).join('\\n') || response.statusText);
  return data;
}
function reportHref(run) {
  if (!run || !run.run_id) return '#';
  return `/reports/runs/${encodeURIComponent(run.run_id)}/ui_image_check_report.html`;
}
function renderRuns(items) {
  document.getElementById('runs').innerHTML = items.map(run => `
    <tr>
      <td>${run.run_id || ''}</td>
      <td>${run.status || ''}</td>
      <td>${run.trigger || ''}</td>
      <td>${run.started_at || ''}</td>
      <td>${run.status === 'success' ? `<a href="${reportHref(run)}">Open</a>` : ''}</td>
    </tr>
  `).join('');
}
async function refresh() {
  const data = await fetchJson('/api/status');
  document.getElementById('statusText').textContent = `Status: ${data.status}`;
  document.getElementById('nextRun').textContent = `Next scheduled run: ${data.next_scheduled_run || '-'}`;
  document.getElementById('runNow').disabled = data.status === 'running';
  document.getElementById('daily_run_time').value = data.config.daily_run_time;
  document.getElementById('history_success_limit').value = data.config.history_success_limit;
  document.getElementById('history_failed_limit').value = data.config.history_failed_limit;
  document.getElementById('ocr_archive_retention_days').value = data.config.ocr_archive_retention_days;
  const latest = (data.successful_runs || []).find(run => run.run_id === data.latest_success_run_id);
  const report = document.getElementById('currentReport');
  if (latest) {
    report.href = reportHref(latest);
    report.style.display = '';
  } else {
    report.style.display = 'none';
  }
  renderRuns([...(data.successful_runs || []), ...(data.failed_runs || [])]);
  document.getElementById('rawStatus').textContent = JSON.stringify(data, null, 2);
}
async function runNow() {
  document.getElementById('runNow').disabled = true;
  try {
    await fetchJson('/api/runs', { method: 'POST' });
  } finally {
    await refresh();
  }
}
async function saveConfig() {
  await fetchJson('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      daily_run_time: document.getElementById('daily_run_time').value,
      history_success_limit: Number(document.getElementById('history_success_limit').value),
      history_failed_limit: Number(document.getElementById('history_failed_limit').value),
      ocr_archive_retention_days: Number(document.getElementById('ocr_archive_retention_days').value)
    })
  });
  await refresh();
}
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""


class ReportServiceHandler(BaseHTTPRequestHandler):
    config: ServiceConfig
    config_path: Path
    runner: ReportRunner
    get_next_run_text: Callable[[], str | None]

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send_text(build_console_html(), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/status":
            self._send_json(status_payload(self.config, self.runner.active_run_id, self.get_next_run_text()))
            return
        if parsed.path == "/api/runs":
            self._send_json(load_index(Path(self.config.reports_dir)))
            return
        if parsed.path.startswith("/reports/"):
            self._serve_report_file(parsed.path)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/api/runs":
                errors = validate_config(self.config)
                if errors:
                    self._send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
                    return
                try:
                    metadata = self.runner.run_once("manual")
                except RuntimeError as exc:
                    self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.CONFLICT)
                    return
                self._send_json({"ok": True, "run": metadata.to_dict()}, status=HTTPStatus.ACCEPTED)
                return
            if parsed.path == "/api/config":
                self._handle_config_update()
                return
            if parsed.path.endswith("/api/ocr-cache/operation"):
                self._handle_ocr_operation()
                return
            self.send_error(HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"ok": False, "error": str(exc)}, status=HTTPStatus.BAD_REQUEST)

    def _handle_config_update(self) -> None:
        data = self._read_json()
        candidate = ServiceConfig(**self.config.to_dict())
        if "daily_run_time" in data:
            candidate.daily_run_time = str(data["daily_run_time"])
        for key in ("history_success_limit", "history_failed_limit", "ocr_archive_retention_days"):
            if key in data:
                try:
                    setattr(candidate, key, int(data[key]))
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{key} must be an integer") from exc

        errors = validate_config(candidate)
        if errors:
            self._send_json({"ok": False, "errors": errors}, status=HTTPStatus.BAD_REQUEST)
            return
        self.config.daily_run_time = candidate.daily_run_time
        self.config.history_success_limit = candidate.history_success_limit
        self.config.history_failed_limit = candidate.history_failed_limit
        self.config.ocr_archive_retention_days = candidate.ocr_archive_retention_days
        save_config(self.config_path, self.config)
        self._send_json({"ok": True, "config": self.config.to_dict()})

    def _handle_ocr_operation(self) -> None:
        data = self._read_json()
        relative_path = str(data.get("relative_path") or data.get("relativePath") or "").strip()
        file_md5 = str(data.get("md5") or "").strip()
        operation = str(data["operation"]) if "operation" in data else check_i18n_images.OCR_OPERATION_IGNORE
        if not relative_path or not file_md5:
            self._send_json({"ok": False, "error": "relative_path and md5 are required"}, status=HTTPStatus.BAD_REQUEST)
            return
        check_i18n_images.update_ocr_cache_operation_sqlite(
            Path(check_i18n_images.OCR_CACHE_DB_FILE),
            relative_path,
            file_md5,
            operation,
        )
        self._send_json({"ok": True})

    def _serve_report_file(self, request_path: str) -> None:
        relative = urllib.parse.unquote(request_path.removeprefix("/reports/")).replace("\\", "/")
        reports_root = Path(self.config.reports_dir).resolve()
        target = (reports_root / relative).resolve()
        if target == reports_root or reports_root not in target.parents or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self._send_bytes(target.read_bytes(), content_type)

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        data = json.loads(raw.decode("utf-8") or "{}")
        if not isinstance(data, dict):
            raise ValueError("request body must be a JSON object")
        return data

    def _send_json(self, data: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_text(self, text: str, content_type: str) -> None:
        self._send_bytes(text.encode("utf-8"), content_type)

    def _send_bytes(self, payload: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def create_server(
    config: ServiceConfig,
    config_path: Path,
    runner: ReportRunner,
    get_next_run_text: Callable[[], str | None],
) -> ThreadingHTTPServer:
    class BoundHandler(ReportServiceHandler):
        pass

    BoundHandler.config = config
    BoundHandler.config_path = config_path
    BoundHandler.runner = runner
    BoundHandler.get_next_run_text = staticmethod(get_next_run_text)
    return ThreadingHTTPServer((config.host, config.port), BoundHandler)
