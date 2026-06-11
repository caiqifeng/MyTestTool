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
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ART SCANNER</title>
<style>
:root { --bg:#f3f6fb; --nav:#131a22; --nav-2:#1b2430; --brand:#08caa6; --text:#182235; --muted:#7b8aa1; --line:#dfe6ef; --panel:#fff; --blue:#2d6cdf; --green:#16a36a; --red:#e5484d; --orange:#f27a3d; }
* { box-sizing:border-box; }
body { margin:0; min-height:100vh; font-family:"Microsoft YaHei","Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--text); }
.app { display:grid; grid-template-columns:188px 1fr; min-height:100vh; }
.side { background:var(--nav); color:#d8e0ea; display:flex; flex-direction:column; border-right:1px solid #263241; }
.brand { height:58px; display:flex; align-items:center; gap:10px; padding:0 16px; border-bottom:1px solid #263241; }
.brand-mark { width:24px; height:24px; border-radius:4px; background:var(--brand); color:#09221d; display:grid; place-items:center; font-weight:800; }
.brand strong { display:block; color:var(--brand); font-size:12px; letter-spacing:1px; }
.brand span { display:block; color:#8fa0b5; font-size:10px; margin-top:2px; }
.nav { padding:14px 10px; display:grid; gap:6px; }
.nav button { width:100%; height:36px; border:0; border-radius:4px; padding:0 12px; text-align:left; background:transparent; color:#c7d2df; font-weight:700; cursor:pointer; }
.nav button.active { background:var(--brand); color:#081d19; }
.side-foot { margin-top:auto; padding:14px 18px; border-top:1px solid #263241; color:#738196; font-size:11px; }
.content { min-width:0; padding:26px 28px 40px; }
.view { display:none; }
.view.active { display:block; }
.page-head { display:flex; justify-content:space-between; gap:16px; align-items:flex-start; margin-bottom:18px; }
.page-title { margin:0; font-size:22px; }
.page-subtitle { margin:6px 0 0; color:var(--muted); font-size:13px; }
.panel { background:var(--panel); border:1px solid var(--line); border-radius:6px; margin-bottom:16px; overflow:hidden; }
.panel-pad { padding:16px; }
.metric-grid { display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:14px; margin-bottom:16px; }
.metric { background:var(--panel); border:1px solid var(--line); border-radius:6px; padding:14px 16px; }
.metric span { display:block; color:var(--muted); font-size:12px; }
.metric strong { display:block; margin-top:6px; font-size:30px; line-height:1; color:var(--blue); }
.metric strong.warn { color:#f05a28; }
.metric strong.ok { color:var(--green); }
.status-pill { display:inline-flex; align-items:center; gap:6px; min-height:24px; padding:3px 10px; border-radius:999px; background:#eef2f7; color:#66758a; font-size:12px; font-weight:700; }
.status-dot { width:6px; height:6px; border-radius:50%; background:#a8b3c3; }
.status-running .status-dot { background:var(--blue); }
.button { border:0; border-radius:5px; background:var(--blue); color:#fff; padding:9px 14px; font-weight:700; cursor:pointer; }
.button:disabled { opacity:.55; cursor:not-allowed; }
.button.secondary { background:#eef4ff; color:#235bc4; }
.latest-frame { width:100%; height:calc(100vh - 198px); min-height:560px; border:0; background:#fff; }
.empty { padding:30px; text-align:center; color:var(--muted); }
table { width:100%; border-collapse:collapse; }
th,td { border-bottom:1px solid #e9eef5; padding:11px 14px; text-align:left; font-size:13px; }
th { background:#f7f9fc; color:#6d7d93; font-weight:700; }
.tag { display:inline-flex; min-height:22px; align-items:center; border-radius:4px; padding:2px 8px; font-size:12px; font-weight:700; }
.tag.success { background:#e8f8ef; color:var(--green); }
.tag.failed { background:#ffeceb; color:var(--red); }
.tag.manual { background:#eaf2ff; color:var(--blue); }
.tag.schedule { background:#e8f8ef; color:var(--green); }
.issue { color:#f05a28; font-weight:700; }
.settings-grid { display:grid; grid-template-columns:260px 1fr; gap:14px; align-items:center; max-width:720px; }
label { color:#526176; font-size:13px; font-weight:700; }
input { width:100%; height:34px; border:1px solid #cfd8e6; border-radius:5px; padding:6px 9px; font:inherit; }
input[type="checkbox"] { width:auto; height:auto; }
.weekday-row { display:flex; gap:8px; flex-wrap:wrap; }
.weekday-button { min-width:46px; height:30px; border:1px solid #cfd8e6; background:#f8fbff; color:#66758a; border-radius:5px; font-weight:700; cursor:pointer; }
.weekday-button.active { border-color:var(--blue); background:var(--blue); color:#fff; }
.trend { display:flex; gap:10px; align-items:end; height:118px; padding:18px; }
.trend-item { flex:1; min-width:48px; display:grid; gap:6px; align-content:end; color:#8a98ac; font-size:11px; text-align:center; }
.trend-bar { height:12px; border-radius:3px; background:var(--blue); }
.trend-bar.warn { background:var(--orange); }
.trend-bar.fail { background:var(--red); }
.cron { margin-top:14px; background:#172134; color:#6dd3ff; border-radius:5px; padding:14px 16px; font-family:Consolas,monospace; }
.toolbar { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:14px 16px; border-bottom:1px solid var(--line); }
.toolbar-actions { display:flex; gap:8px; align-items:center; }
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="brand"><div class="brand-mark">A</div><div><strong>ART SCANNER</strong><span>美术资源巡检工具</span></div></div>
    <nav class="nav">
      <button class="active" data-view="latest" onclick="showView('latest')">最新结果</button>
      <button data-view="tasks" onclick="showView('tasks')">任务管理</button>
      <button data-view="history" onclick="showView('history')">历史记录</button>
      <button data-view="settings" onclick="showView('settings')">定时设置</button>
    </nav>
    <div class="side-foot">v1.0.0 · 2026-06-11</div>
  </aside>
  <main class="content">
    <section id="view-latest" class="view active">
      <div class="page-head">
        <div><h1 class="page-title">最新结果</h1><p class="page-subtitle">展示最近一次成功生成的检查报告。</p></div>
        <div><span id="latestIssueCount" class="metric-count">-</span></div>
      </div>
      <div class="panel">
        <div class="toolbar">
          <strong>报告详情</strong>
          <div class="toolbar-actions"><a id="currentReport" class="button secondary" href="#" target="_blank" style="display:none">打开最新报告</a></div>
        </div>
        <div id="latestEmpty" class="empty">暂无成功报告</div>
        <iframe id="latestReportFrame" class="latest-frame" title="最新检查报告" style="display:none"></iframe>
      </div>
    </section>
    <section id="view-tasks" class="view">
      <div class="page-head"><div><h1 class="page-title">任务管理</h1><p class="page-subtitle">管理美术资源图片扫描任务，立即运行或查看执行记录。</p></div></div>
      <div class="metric-grid">
        <div class="metric"><span>最近扫描数</span><strong id="latestScanCount">-</strong></div>
        <div class="metric"><span>最近问题数</span><strong id="latestProblemCount" class="warn">-</strong></div>
        <div class="metric"><span>服务状态</span><strong id="serviceState" class="ok">-</strong></div>
        <div class="metric"><span>历史执行次数</span><strong id="runTotal">-</strong></div>
      </div>
      <div class="panel panel-pad">
        <div class="page-head"><div><h2 class="page-title">立即运行</h2><p class="page-subtitle">启动全量美术资源扫描，生成最新报告。</p></div><span id="statusText" class="status-pill"><span class="status-dot"></span>加载中</span></div>
        <button id="runNow" class="button" onclick="runNow()">立即运行扫描</button>
        <p id="nextRun" class="page-subtitle"></p>
      </div>
      <div class="panel">
        <div class="toolbar"><strong>近期执行记录</strong></div>
        <table><thead><tr><th>状态</th><th>触发方式</th><th>开始时间</th><th>结束时间</th><th>扫描图数</th><th>问题数</th><th>报告</th></tr></thead><tbody id="runs"></tbody></table>
      </div>
    </section>
    <section id="view-history" class="view">
      <div class="page-head"><div><h1 class="page-title">历史记录</h1><p class="page-subtitle">历史报告为只读，仅用于追溯查看。</p></div><span id="historySummary" class="status-pill">-</span></div>
      <div class="panel"><div class="toolbar"><strong>问题数趋势（近7次）</strong></div><div id="historyTrend" class="trend"></div></div>
      <div class="panel"><table><thead><tr><th>状态</th><th>日期</th><th>时间</th><th>触发</th><th>扫描图数</th><th>问题</th><th>耗时</th><th>报告</th></tr></thead><tbody id="historyRows"></tbody></table></div>
    </section>
    <section id="view-settings" class="view">
      <div class="page-head"><div><h1 class="page-title">定时设置</h1><p class="page-subtitle">配置自动扫描任务的执行计划。</p></div></div>
      <div class="panel panel-pad">
        <div class="settings-grid">
          <label for="schedule_enabled">启用定时任务</label><div><input id="schedule_enabled" name="schedule_enabled" type="checkbox"></div>
          <label for="daily_run_time">每日执行时刻</label><input id="daily_run_time" name="daily_run_time" value="02:00">
          <label>执行日期</label><div class="weekday-row" id="schedule_weekdays">
            <button class="weekday-button" type="button" data-weekday="0" onclick="toggleWeekday(0)">周一</button>
            <button class="weekday-button" type="button" data-weekday="1" onclick="toggleWeekday(1)">周二</button>
            <button class="weekday-button" type="button" data-weekday="2" onclick="toggleWeekday(2)">周三</button>
            <button class="weekday-button" type="button" data-weekday="3" onclick="toggleWeekday(3)">周四</button>
            <button class="weekday-button" type="button" data-weekday="4" onclick="toggleWeekday(4)">周五</button>
            <button class="weekday-button" type="button" data-weekday="5" onclick="toggleWeekday(5)">周六</button>
            <button class="weekday-button" type="button" data-weekday="6" onclick="toggleWeekday(6)">周日</button>
          </div>
          <label for="history_success_limit">成功历史保留数量</label><input id="history_success_limit" name="history_success_limit" type="number" value="5">
          <label for="history_failed_limit">失败历史保留数量</label><input id="history_failed_limit" name="history_failed_limit" type="number" value="5">
          <label for="ocr_archive_retention_days">OCR 归档保留天数</label><input id="ocr_archive_retention_days" name="ocr_archive_retention_days" type="number" value="30">
        </div>
        <div id="cronPreview" class="cron">-</div>
        <p><button class="button" onclick="saveConfig()">保存设置</button></p>
      </div>
    </section>
  </main>
</div>
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
function showView(name) {
  document.querySelectorAll('.view').forEach(view => view.classList.toggle('active', view.id === `view-${name}`));
  document.querySelectorAll('.nav button').forEach(button => button.classList.toggle('active', button.dataset.view === name));
}
function statusTag(run) {
  const ok = run.status === 'success';
  return `<span class="tag ${ok ? 'success' : 'failed'}">${ok ? '成功' : '失败'}</span>`;
}
function triggerTag(run) {
  const manual = run.trigger === 'manual';
  return `<span class="tag ${manual ? 'manual' : 'schedule'}">${manual ? '手动' : '定时'}</span>`;
}
function issueCount(run) {
  const counts = run.counts || {};
  return Number(counts.findings || counts.problem_count || counts.abnormal_count || 0);
}
function scanCount(run) {
  const counts = run.counts || {};
  return Number(counts.i18n_count || 0) + Number(counts.mainland_count || 0);
}
function formatDuration(run) {
  const seconds = Number(run.duration_seconds || 0);
  if (!seconds) return '-';
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  return minutes ? `${minutes}m ${rest}s` : `${rest}s`;
}
function datePart(value) {
  return String(value || '').slice(0, 10) || '-';
}
function timePart(value) {
  return String(value || '').slice(11, 19) || '-';
}
function renderRuns(items) {
  document.getElementById('runs').innerHTML = items.map(run => `
    <tr>
      <td>${statusTag(run)}</td>
      <td>${triggerTag(run)}</td>
      <td>${run.started_at || ''}</td>
      <td>${run.finished_at || ''}</td>
      <td>${scanCount(run).toLocaleString()}</td>
      <td class="issue">${issueCount(run) || '-'}</td>
      <td>${run.status === 'success' ? `<a href="${reportHref(run)}" target="_blank">查看</a>` : (run.error_summary || '')}</td>
    </tr>
  `).join('');
}
function renderHistory(items) {
  document.getElementById('historyRows').innerHTML = items.map(run => `
    <tr>
      <td>${statusTag(run)}</td>
      <td>${datePart(run.started_at)}</td>
      <td>${timePart(run.started_at)} → ${timePart(run.finished_at)}</td>
      <td>${triggerTag(run)}</td>
      <td>${scanCount(run).toLocaleString()}</td>
      <td class="issue">${run.status === 'success' ? (issueCount(run) || '-') : '中断'}</td>
      <td>${formatDuration(run)}</td>
      <td>${run.status === 'success' ? `<a href="${reportHref(run)}" target="_blank">只读查看</a>` : ''}</td>
    </tr>
  `).join('');
}
function renderHistoryTrend(items) {
  const recent = items.slice(0, 7).reverse();
  const maxIssues = Math.max(1, ...recent.map(issueCount));
  document.getElementById('historyTrend').innerHTML = recent.map(run => {
    const issues = issueCount(run);
    const height = Math.max(10, Math.round((issues / maxIssues) * 82));
    const cls = run.status !== 'success' ? 'fail' : issues > 20 ? 'warn' : '';
    return `<div class="trend-item"><div class="trend-bar ${cls}" style="height:${height}px"></div><span>${datePart(run.started_at).slice(5)}</span><strong>${run.status === 'success' ? issues : '失败'}</strong></div>`;
  }).join('');
}
function selectedWeekdays() {
  return Array.from(document.querySelectorAll('.weekday-button.active')).map(button => Number(button.dataset.weekday));
}
function setWeekdays(values) {
  const selected = new Set((values || []).map(Number));
  document.querySelectorAll('.weekday-button').forEach(button => {
    button.classList.toggle('active', selected.has(Number(button.dataset.weekday)));
  });
}
function toggleWeekday(day) {
  const button = document.querySelector(`.weekday-button[data-weekday="${day}"]`);
  if (button) button.classList.toggle('active');
  renderCronPreview(document.getElementById('daily_run_time').value);
}
function renderCronPreview(value) {
  const parts = String(value || '02:00').split(':');
  const weekdays = selectedWeekdays();
  document.getElementById('cronPreview').textContent = document.getElementById('schedule_enabled').checked
    ? `${parts[1] || '00'} ${parts[0] || '02'} * * ${weekdays.length ? weekdays.join(',') : '-'}`
    : '定时任务已停用';
}
async function refresh() {
  const data = await fetchJson('/api/status');
  const running = data.status === 'running';
  document.getElementById('statusText').classList.toggle('status-running', running);
  document.getElementById('statusText').innerHTML = `<span class="status-dot"></span>${running ? '运行中' : '待机'}`;
  document.getElementById('serviceState').textContent = running ? '运行中' : '待机';
  document.getElementById('nextRun').textContent = `下次定时执行：${data.next_scheduled_run || '-'}`;
  document.getElementById('runNow').disabled = data.status === 'running';
  document.getElementById('daily_run_time').value = data.config.daily_run_time;
  document.getElementById('schedule_enabled').checked = Boolean(data.config.schedule_enabled);
  setWeekdays(data.config.schedule_weekdays || []);
  document.getElementById('history_success_limit').value = data.config.history_success_limit;
  document.getElementById('history_failed_limit').value = data.config.history_failed_limit;
  document.getElementById('ocr_archive_retention_days').value = data.config.ocr_archive_retention_days;
  renderCronPreview(data.config.daily_run_time);
  const latest = (data.successful_runs || []).find(run => run.run_id === data.latest_success_run_id);
  const report = document.getElementById('currentReport');
  const frame = document.getElementById('latestReportFrame');
  const empty = document.getElementById('latestEmpty');
  if (latest) {
    report.href = reportHref(latest);
    report.style.display = '';
    frame.src = reportHref(latest);
    frame.style.display = '';
    empty.style.display = 'none';
    document.getElementById('latestIssueCount').innerHTML = `<span class="page-subtitle">本地待处理图数</span><br><strong>${issueCount(latest)}</strong>`;
    document.getElementById('latestScanCount').textContent = scanCount(latest).toLocaleString();
    document.getElementById('latestProblemCount').textContent = String(issueCount(latest));
  } else {
    report.style.display = 'none';
    frame.style.display = 'none';
    empty.style.display = '';
    document.getElementById('latestIssueCount').textContent = '-';
    document.getElementById('latestScanCount').textContent = '-';
    document.getElementById('latestProblemCount').textContent = '-';
  }
  const allRuns = [...(data.successful_runs || []), ...(data.failed_runs || [])];
  document.getElementById('runTotal').textContent = String(allRuns.length);
  document.getElementById('historySummary').textContent = `共 ${allRuns.length} 次 · ${data.successful_runs.length} 成功 · ${data.failed_runs.length} 失败`;
  renderRuns(allRuns.slice(0, 5));
  renderHistory(allRuns);
  renderHistoryTrend(allRuns);
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
      schedule_enabled: document.getElementById('schedule_enabled').checked,
      schedule_weekdays: selectedWeekdays(),
      history_success_limit: Number(document.getElementById('history_success_limit').value),
      history_failed_limit: Number(document.getElementById('history_failed_limit').value),
      ocr_archive_retention_days: Number(document.getElementById('ocr_archive_retention_days').value)
    })
  });
  await refresh();
}
document.getElementById('daily_run_time').addEventListener('input', event => renderCronPreview(event.target.value));
document.getElementById('schedule_enabled').addEventListener('change', () => renderCronPreview(document.getElementById('daily_run_time').value));
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
        if "schedule_enabled" in data:
            candidate.schedule_enabled = bool(data["schedule_enabled"])
        if "schedule_weekdays" in data:
            raw_weekdays = data["schedule_weekdays"]
            if not isinstance(raw_weekdays, list):
                raise ValueError("schedule_weekdays must be a list")
            try:
                candidate.schedule_weekdays = [int(day) for day in raw_weekdays]
            except (TypeError, ValueError) as exc:
                raise ValueError("schedule_weekdays values must be integers") from exc
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
        self.config.schedule_enabled = candidate.schedule_enabled
        self.config.schedule_weekdays = candidate.schedule_weekdays
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
