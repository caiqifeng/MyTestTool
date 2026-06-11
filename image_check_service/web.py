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
    active_run: dict[str, object] | None = None,
    config_errors: list[str] | None = None,
    local_report_path: Path | None = None,
) -> dict[str, object]:
    index = load_index(Path(config.reports_dir))
    latest_report_url = None
    latest_success_run_id = index.get("latest_success_run_id")
    successful_runs = list(index.get("successful_runs", []))
    if latest_success_run_id:
        latest_report_url = f"/reports/runs/{urllib.parse.quote(str(latest_success_run_id))}/ui_image_check_report.html"
    elif local_report_path is not None and local_report_path.is_file():
        latest_report_url = "/local/ui_image_check_report.html"
        latest_success_run_id = "local"
        successful_runs = [
            {
                "run_id": "local",
                "trigger": "local",
                "status": "success",
                "started_at": "",
                "finished_at": "",
                "duration_seconds": None,
                "report_path": str(local_report_path),
                "log_path": None,
                "error_summary": None,
                "counts": {},
            }
        ]
    return {
        "status": "running" if active_run_id else "idle",
        "active_run_id": active_run_id,
        "active_run": active_run,
        "next_scheduled_run": next_run_text,
        "latest_success_run_id": latest_success_run_id,
        "latest_report_url": latest_report_url,
        "successful_runs": successful_runs,
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
<title>《剑网3》重制版 - 多语言翻译检查平台</title>
<style>
:root { --bg:#f3f6fb; --nav:#131a22; --nav-2:#1b2430; --brand:#08caa6; --text:#182235; --muted:#7b8aa1; --line:#dfe6ef; --panel:#fff; --blue:#2d6cdf; --green:#16a36a; --red:#e5484d; --orange:#f27a3d; }
* { box-sizing:border-box; }
body { margin:0; min-height:100vh; font-family:"Microsoft YaHei","Segoe UI",Arial,sans-serif; background:var(--bg); color:var(--text); }
.app { display:grid; grid-template-columns:188px 1fr; min-height:100vh; }
.side { background:var(--nav); color:#d8e0ea; display:flex; flex-direction:column; border-right:1px solid #263241; }
.brand { height:58px; display:flex; align-items:center; gap:10px; padding:0 14px; border-bottom:1px solid #263241; }
.brand-mark { width:32px; height:32px; flex:0 0 32px; display:block; object-fit:contain; }
.brand strong { display:block; color:var(--brand); font-size:13px; line-height:1.2; letter-spacing:0; white-space:nowrap; }
.brand span { display:block; color:#8fa0b5; font-size:10px; line-height:1.25; margin-top:2px; white-space:nowrap; }
.nav { padding:14px 10px; display:grid; gap:6px; }
.nav button { width:100%; height:36px; border:0; border-radius:4px; padding:0 12px; text-align:left; background:transparent; color:#c7d2df; font-weight:700; cursor:pointer; }
.nav button.active { background:var(--brand); color:#081d19; }
.side-foot { margin-top:auto; padding:14px 18px; border-top:1px solid #263241; color:#738196; font-size:11px; }
.content { min-width:0; height:100vh; overflow:hidden; padding:26px 28px 40px; }
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
.dialog-backdrop { position:fixed; inset:0; z-index:50; display:none; align-items:center; justify-content:center; background:rgba(15,23,42,.38); padding:24px; }
.dialog-backdrop.open { display:flex; }
.dialog { width:min(420px, 100%); border-radius:8px; background:#fff; box-shadow:0 18px 52px rgba(15,23,42,.24); overflow:hidden; }
.dialog-head { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:16px 18px; border-bottom:1px solid var(--line); }
.dialog-title { margin:0; font-size:17px; }
.dialog-close { border:0; background:transparent; color:#7b8aa1; font-size:22px; line-height:1; cursor:pointer; }
.dialog-body { padding:18px; color:#405069; font-size:14px; line-height:1.55; word-break:break-word; }
.dialog.success .dialog-title { color:var(--green); }
.dialog.error .dialog-title { color:var(--red); }
.dialog-actions { display:flex; justify-content:flex-end; padding:0 18px 18px; }
.latest-report-panel { height:100vh; border:0; border-radius:0; margin:0; display:flex; flex-direction:column; }
.latest-frame { flex:1 1 auto; width:100%; min-height:0; border:0; background:#fff; }
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
select { width:100%; height:34px; border:1px solid #cfd8e6; border-radius:5px; padding:6px 9px; font:inherit; background:#fff; }
.param-grid { display:grid; grid-template-columns:180px 1fr; gap:12px; align-items:center; }
.param-help { margin:4px 0 0; color:var(--muted); font-size:12px; }
.advanced-params { max-width:860px; margin:12px 0 14px; border:1px solid #dbe4f0; border-radius:6px; background:#fbfdff; overflow:hidden; }
.advanced-toggle { width:100%; height:42px; border:0; background:#f7faff; color:#334155; display:flex; align-items:center; justify-content:space-between; padding:0 14px; font-weight:700; cursor:pointer; }
.advanced-toggle span { color:var(--muted); font-weight:600; font-size:12px; }
.advanced-body { display:none; padding:14px; border-top:1px solid #e4ebf4; }
.advanced-params.open .advanced-body { display:block; }
.advanced-params.open .advanced-toggle span::after { content:"收起"; }
.advanced-params:not(.open) .advanced-toggle span::after { content:"展开"; }
.schedule-switch { display:inline-grid; grid-template-columns:1fr 1fr; position:relative; width:132px; height:34px; padding:3px; border-radius:999px; background:#e8eef6; border:1px solid #d3deec; vertical-align:middle; }
.schedule-switch::before { content:""; position:absolute; top:3px; bottom:3px; width:61px; border-radius:999px; background:#fff; box-shadow:0 1px 4px rgba(15,23,42,.16); transition:left .16s ease; }
.schedule-switch[data-enabled="true"]::before { left:3px; }
.schedule-switch[data-enabled="false"]::before { left:66px; }
.schedule-switch button { position:relative; z-index:1; border:0; background:transparent; color:#64748b; font-weight:800; cursor:pointer; }
.schedule-switch button.active { color:var(--blue); }
.schedule-state { margin-left:10px; color:var(--muted); font-size:13px; font-weight:700; }
.weekday-row { display:flex; gap:8px; flex-wrap:wrap; }
.weekday-button { min-width:46px; height:30px; border:1px solid #cfd8e6; background:#f8fbff; color:#66758a; border-radius:5px; font-weight:700; cursor:pointer; }
.weekday-button.active { border-color:var(--blue); background:var(--blue); color:#fff; }
.trend { display:flex; gap:10px; align-items:end; height:118px; padding:18px; }
.trend-item { flex:1; min-width:48px; display:grid; gap:6px; align-content:end; color:#8a98ac; font-size:11px; text-align:center; }
.trend-bar { height:12px; border-radius:3px; background:var(--blue); }
.trend-bar.warn { background:var(--orange); }
.trend-bar.fail { background:var(--red); }
.run-detail-grid { display:grid; grid-template-columns:repeat(3, minmax(0,1fr)); gap:12px; margin-top:14px; }
.run-detail { background:#f7f9fc; border:1px solid #e4ebf4; border-radius:5px; padding:10px 12px; }
.run-detail span { display:block; color:var(--muted); font-size:12px; }
.run-detail strong { display:block; margin-top:4px; font-size:13px; word-break:break-all; }
.log-view { margin-top:14px; min-height:180px; max-height:360px; overflow:auto; background:#111827; color:#d1e7ff; border-radius:5px; padding:12px; font:12px/1.55 Consolas,monospace; white-space:pre-wrap; }
.cron { margin-top:14px; background:#172134; color:#6dd3ff; border-radius:5px; padding:14px 16px; font-family:Consolas,monospace; }
.toolbar { display:flex; justify-content:space-between; gap:12px; align-items:center; padding:14px 16px; border-bottom:1px solid var(--line); }
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="brand"><img class="brand-mark" src="/static/app-icon.png" alt=""><div><strong>《剑网3》重制版</strong><span>多语言翻译检查平台</span></div></div>
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
      <div class="panel latest-report-panel">
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
        <div class="advanced-params" data-advanced-panel>
          <button class="advanced-toggle" type="button" onclick="toggleAdvancedParams(this)">高级运行参数：默认参数运行<span></span></button>
          <div class="advanced-body">
            <div class="param-grid">
              <label for="task_check_config">--config</label><div><input id="task_check_config" data-config-field="check_config" value="check_config.json"><p class="param-help">JSON 配置文件路径，默认使用脚本同级目录 check_config.json</p></div>
              <label for="task_i18n">--i18n</label><div><input id="task_i18n" data-advanced-field="i18n"><p class="param-help">国际版图片目录路径（与 --mainland 配对，或使用 --config）</p></div>
              <label for="task_mainland">--mainland</label><div><input id="task_mainland" data-advanced-field="mainland"><p class="param-help">陆版图片目录路径（与 --i18n 配对，或使用 --config）</p></div>
              <label for="task_output">--output</label><div><input id="task_output" data-advanced-field="output"><p class="param-help">输出文件路径；管理服务运行时默认写入历史运行目录</p></div>
              <label for="task_since">--since</label><div><input id="task_since" data-advanced-field="since" placeholder="2026-05-27T00:00:00+08:00"><p class="param-help">只检查此时间后的陆版新增图片</p></div>
              <label for="task_no_ocr">--no-ocr</label><select id="task_no_ocr" data-advanced-field="no_ocr" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
              <label for="task_ocr_workers">--ocr-workers</label><div><input id="task_ocr_workers" data-config-field="ocr_workers" type="number" min="1" value="1"><p class="param-help">OCR 并发线程数，默认 1</p></div>
              <label for="task_max_files">--max-files</label><input id="task_max_files" data-advanced-field="max_files" data-advanced-type="number" type="number" min="1">
              <label for="task_assume_new_has_text">--assume-new-has-text</label><select id="task_assume_new_has_text" data-advanced-field="assume_new_has_text" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
              <label for="task_max_image_px">--max-image-px</label><input id="task_max_image_px" data-advanced-field="max_image_px" data-advanced-type="number" type="number" min="1" placeholder="720">
              <label for="task_serve_report">--serve-report</label><select id="task_serve_report" data-advanced-field="serve_report" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
              <label for="task_no_serve_report">--no-serve-report</label><select id="task_no_serve_report" data-advanced-field="no_serve_report" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
              <label for="task_report_server_only">--report-server-only</label><select id="task_report_server_only" data-advanced-field="report_server_only" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
              <label for="task_serve_host">--serve-host</label><input id="task_serve_host" data-advanced-field="serve_host" placeholder="0.0.0.0">
              <label for="task_serve_port">--serve-port</label><input id="task_serve_port" data-advanced-field="serve_port" data-advanced-type="number" type="number" min="1" placeholder="9080">
            </div>
          </div>
        </div>
        <p><button class="button secondary" onclick="saveConfig()">保存执行参数</button></p>
        <button id="runNow" class="button" onclick="runNow()">立即运行扫描</button>
        <p id="nextRun" class="page-subtitle"></p>
        <div class="run-detail-grid">
          <div class="run-detail"><span>当前运行 ID</span><strong id="activeRunId">-</strong></div>
          <div class="run-detail"><span>触发方式</span><strong id="activeRunTrigger">-</strong></div>
          <div class="run-detail"><span>开始时间</span><strong id="activeRunStarted">-</strong></div>
        </div>
        <pre id="activeRunLog" class="log-view">暂无运行日志</pre>
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
          <label>启用定时任务</label><div><div class="schedule-switch" id="schedule_enabled" data-enabled="true">
            <button type="button" data-schedule-value="true" onclick="setScheduleEnabled(true)">开</button>
            <button type="button" data-schedule-value="false" onclick="setScheduleEnabled(false)">关</button>
          </div><span id="scheduleStateText" class="schedule-state">当前：已启用</span></div>
          <label for="daily_run_time">每日执行时刻</label><input id="daily_run_time" name="daily_run_time" value="02:00">
          <label>运行参数</label><div class="advanced-params" data-advanced-panel>
            <button class="advanced-toggle" type="button" onclick="toggleAdvancedParams(this)">高级运行参数：默认参数运行<span></span></button>
            <div class="advanced-body">
              <div class="param-grid">
                <label for="settings_check_config">--config</label><div><input id="settings_check_config" data-config-field="check_config" value="check_config.json"><p class="param-help">JSON 配置文件路径，默认使用脚本同级目录 check_config.json</p></div>
                <label for="settings_i18n">--i18n</label><input id="settings_i18n" data-advanced-field="i18n">
                <label for="settings_mainland">--mainland</label><input id="settings_mainland" data-advanced-field="mainland">
                <label for="settings_output">--output</label><input id="settings_output" data-advanced-field="output">
                <label for="settings_since">--since</label><input id="settings_since" data-advanced-field="since" placeholder="2026-05-27T00:00:00+08:00">
                <label for="settings_no_ocr">--no-ocr</label><select id="settings_no_ocr" data-advanced-field="no_ocr" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
                <label for="settings_ocr_workers">--ocr-workers</label><input id="settings_ocr_workers" data-config-field="ocr_workers" type="number" min="1" value="1">
                <label for="settings_max_files">--max-files</label><input id="settings_max_files" data-advanced-field="max_files" data-advanced-type="number" type="number" min="1">
                <label for="settings_assume_new_has_text">--assume-new-has-text</label><select id="settings_assume_new_has_text" data-advanced-field="assume_new_has_text" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
                <label for="settings_max_image_px">--max-image-px</label><input id="settings_max_image_px" data-advanced-field="max_image_px" data-advanced-type="number" type="number" min="1" placeholder="720">
                <label for="settings_serve_report">--serve-report</label><select id="settings_serve_report" data-advanced-field="serve_report" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
                <label for="settings_no_serve_report">--no-serve-report</label><select id="settings_no_serve_report" data-advanced-field="no_serve_report" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
                <label for="settings_report_server_only">--report-server-only</label><select id="settings_report_server_only" data-advanced-field="report_server_only" data-advanced-type="bool"><option value="">默认</option><option value="true">启用</option></select>
                <label for="settings_serve_host">--serve-host</label><input id="settings_serve_host" data-advanced-field="serve_host" placeholder="0.0.0.0">
                <label for="settings_serve_port">--serve-port</label><input id="settings_serve_port" data-advanced-field="serve_port" data-advanced-type="number" type="number" min="1" placeholder="9080">
              </div>
            </div>
          </div>
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
<div id="saveFeedbackDialog" class="dialog-backdrop" role="dialog" aria-modal="true" aria-labelledby="saveFeedbackTitle" aria-describedby="saveFeedbackMessage">
  <div id="saveFeedbackPanel" class="dialog">
    <div class="dialog-head">
      <h2 id="saveFeedbackTitle" class="dialog-title">保存成功</h2>
      <button class="dialog-close" type="button" aria-label="关闭" onclick="closeSaveFeedback()">×</button>
    </div>
    <div id="saveFeedbackMessage" class="dialog-body"></div>
    <div class="dialog-actions"><button class="button" type="button" onclick="closeSaveFeedback()">确定</button></div>
  </div>
</div>
<script>
const dirtyFields = new Set();
async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || (data.errors || []).join('\\n') || response.statusText);
  return data;
}
function reportHref(run) {
  if (!run || !run.run_id) return '#';
  if (run.report_url) return run.report_url;
  return `/reports/runs/${encodeURIComponent(run.run_id)}/ui_image_check_report.html`;
}
function setLatestReportFrame(frame, url) {
  if (frame.dataset.currentSrc !== url) {
    frame.src = url;
    frame.dataset.currentSrc = url;
  }
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
async function renderActiveRun(activeRun) {
  document.getElementById('activeRunId').textContent = activeRun && activeRun.run_id ? activeRun.run_id : '-';
  document.getElementById('activeRunTrigger').textContent = activeRun && activeRun.trigger ? activeRun.trigger : '-';
  document.getElementById('activeRunStarted').textContent = activeRun && activeRun.started_at ? activeRun.started_at : '-';
  const logBox = document.getElementById('activeRunLog');
  if (!activeRun || !activeRun.run_id) {
    logBox.textContent = '暂无运行日志';
    return;
  }
  try {
    const payload = await fetchJson(`/reports/runs/${encodeURIComponent(activeRun.run_id)}/api/log`);
    logBox.textContent = payload.log || '暂无运行日志';
    logBox.scrollTop = logBox.scrollHeight;
  } catch (error) {
    logBox.textContent = '日志暂不可用';
  }
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
function setScheduleEnabled(enabled) {
  const toggle = document.getElementById('schedule_enabled');
  toggle.dataset.enabled = enabled ? 'true' : 'false';
  toggle.querySelectorAll('button').forEach(button => {
    button.classList.toggle('active', button.dataset.scheduleValue === String(enabled));
  });
  document.getElementById('scheduleStateText').textContent = enabled ? '当前：已启用' : '当前：已停用';
  renderCronPreview(document.getElementById('daily_run_time').value);
}
function scheduleEnabled() {
  return document.getElementById('schedule_enabled').dataset.enabled === 'true';
}
function setInputValueUnlessDirty(input, value) {
  if (dirtyFields.has(input.dataset.dirtyKey || input.id)) return;
  input.value = value;
}
function showSaveFeedback(success, message) {
  const dialog = document.getElementById('saveFeedbackDialog');
  const panel = document.getElementById('saveFeedbackPanel');
  document.getElementById('saveFeedbackTitle').textContent = success ? '保存成功' : '保存失败';
  document.getElementById('saveFeedbackMessage').textContent = message;
  panel.classList.toggle('success', success);
  panel.classList.toggle('error', !success);
  dialog.classList.add('open');
}
function closeSaveFeedback() {
  document.getElementById('saveFeedbackDialog').classList.remove('open');
}
function setExecutionParams(config) {
  document.querySelectorAll('[data-config-field="check_config"]').forEach(input => {
    setInputValueUnlessDirty(input, config.check_config || 'check_config.json');
  });
  document.querySelectorAll('[data-config-field="ocr_workers"]').forEach(input => {
    setInputValueUnlessDirty(input, Number(config.ocr_workers || 1));
  });
  setAdvancedArgs(config.advanced_args || {});
  updateAdvancedSummary();
}
function syncExecutionParam(field, value) {
  document.querySelectorAll(`[data-config-field="${field}"]`).forEach(input => {
    if (String(input.value) !== String(value)) input.value = value;
  });
}
function toggleAdvancedParams(button) {
  button.closest('[data-advanced-panel]').classList.toggle('open');
}
function setAdvancedArgs(values) {
  document.querySelectorAll('[data-advanced-field]').forEach(input => {
    const key = input.dataset.advancedField;
    const value = values[key];
    if (input.dataset.advancedType === 'bool') {
      setInputValueUnlessDirty(input, value === true ? 'true' : '');
    } else {
      setInputValueUnlessDirty(input, value === undefined || value === null ? '' : value);
    }
  });
}
function collectAdvancedArgs() {
  const result = {};
  document.querySelectorAll('#view-settings [data-advanced-field]').forEach(input => {
    const key = input.dataset.advancedField;
    if (Object.prototype.hasOwnProperty.call(result, key)) return;
    if (input.dataset.advancedType === 'bool') {
      if (input.value === 'true') result[key] = true;
    } else if (input.dataset.advancedType === 'number') {
      if (String(input.value).trim()) result[key] = Number(input.value);
    } else if (String(input.value).trim()) {
      result[key] = input.value.trim();
    }
  });
  return result;
}
function syncAdvancedParam(field, value) {
  document.querySelectorAll(`[data-advanced-field="${field}"]`).forEach(input => {
    if (String(input.value) !== String(value)) input.value = value;
  });
  updateAdvancedSummary();
}
function updateAdvancedSummary() {
  const advanced = collectAdvancedArgs();
  const customCount = Object.keys(advanced).length;
  const text = customCount ? `高级运行参数：已设置 ${customCount} 项` : '高级运行参数：默认参数运行';
  document.querySelectorAll('.advanced-toggle').forEach(button => {
    button.firstChild.nodeValue = text;
  });
}
function renderCronPreview(value) {
  const parts = String(value || '02:00').split(':');
  const weekdays = selectedWeekdays();
  document.getElementById('cronPreview').textContent = scheduleEnabled()
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
  setInputValueUnlessDirty(document.getElementById('daily_run_time'), data.config.daily_run_time);
  setScheduleEnabled(Boolean(data.config.schedule_enabled));
  setExecutionParams(data.config);
  setWeekdays(data.config.schedule_weekdays || []);
  setInputValueUnlessDirty(document.getElementById('history_success_limit'), data.config.history_success_limit);
  setInputValueUnlessDirty(document.getElementById('history_failed_limit'), data.config.history_failed_limit);
  setInputValueUnlessDirty(document.getElementById('ocr_archive_retention_days'), data.config.ocr_archive_retention_days);
  renderCronPreview(data.config.daily_run_time);
  const latest = (data.successful_runs || []).find(run => run.run_id === data.latest_success_run_id);
  const latestReportUrl = data.latest_report_url || (latest ? reportHref(latest) : '');
  const frame = document.getElementById('latestReportFrame');
  const empty = document.getElementById('latestEmpty');
  if (latestReportUrl) {
    setLatestReportFrame(frame, latestReportUrl);
    frame.style.display = '';
    empty.style.display = 'none';
    document.getElementById('latestScanCount').textContent = scanCount(latest).toLocaleString();
    document.getElementById('latestProblemCount').textContent = String(issueCount(latest));
  } else {
    frame.style.display = 'none';
    frame.removeAttribute('src');
    delete frame.dataset.currentSrc;
    empty.style.display = '';
    document.getElementById('latestScanCount').textContent = '-';
    document.getElementById('latestProblemCount').textContent = '-';
  }
  const allRuns = [...(data.successful_runs || []), ...(data.failed_runs || [])];
  document.getElementById('runTotal').textContent = String(allRuns.length);
  document.getElementById('historySummary').textContent = `共 ${allRuns.length} 次 · ${data.successful_runs.length} 成功 · ${data.failed_runs.length} 失败`;
  renderRuns(allRuns.slice(0, 5));
  renderHistory(allRuns);
  renderHistoryTrend(allRuns);
  await renderActiveRun(data.active_run);
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
  try {
    await fetchJson('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        daily_run_time: document.getElementById('daily_run_time').value,
        schedule_enabled: scheduleEnabled(),
        check_config: document.getElementById('settings_check_config').value,
        ocr_workers: Number(document.getElementById('settings_ocr_workers').value),
        advanced_args: collectAdvancedArgs(),
        schedule_weekdays: selectedWeekdays(),
        history_success_limit: Number(document.getElementById('history_success_limit').value),
        history_failed_limit: Number(document.getElementById('history_failed_limit').value),
        ocr_archive_retention_days: Number(document.getElementById('ocr_archive_retention_days').value)
      })
    });
    dirtyFields.clear();
    showSaveFeedback(true, '保存成功');
    await refresh();
  } catch (error) {
    showSaveFeedback(false, `保存失败：${error.message || error}`);
  }
}
document.querySelectorAll('input, select').forEach(input => {
  input.dataset.dirtyKey = input.dataset.configField || input.dataset.advancedField || input.id;
  input.addEventListener('input', event => dirtyFields.add(event.target.dataset.dirtyKey || event.target.id));
  input.addEventListener('change', event => dirtyFields.add(event.target.dataset.dirtyKey || event.target.id));
});
document.getElementById('daily_run_time').addEventListener('input', event => renderCronPreview(event.target.value));
document.querySelectorAll('[data-config-field="check_config"]').forEach(input => {
  input.addEventListener('input', event => syncExecutionParam('check_config', event.target.value));
});
document.querySelectorAll('[data-config-field="ocr_workers"]').forEach(input => {
  input.addEventListener('input', event => syncExecutionParam('ocr_workers', event.target.value));
});
document.querySelectorAll('[data-advanced-field]').forEach(input => {
  input.addEventListener('input', event => syncAdvancedParam(event.target.dataset.advancedField, event.target.value));
  input.addEventListener('change', event => syncAdvancedParam(event.target.dataset.advancedField, event.target.value));
});
async function refreshLoop() {
  try {
    await refresh();
  } finally {
    const running = document.getElementById('serviceState').textContent === '运行中';
    setTimeout(refreshLoop, running ? 2000 : 5000);
  }
}
refreshLoop();
</script>
</body>
</html>"""


class ReportServiceHandler(BaseHTTPRequestHandler):
    config: ServiceConfig
    config_path: Path
    runner: ReportRunner
    get_next_run_text: Callable[[], str | None]
    static_root: Path
    app_static_root: Path

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            self._send_text(build_console_html(), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/status":
            self._send_json(status_payload(
                self.config,
                self.runner.active_run_id,
                self.get_next_run_text(),
                active_run=self.runner.active_run_snapshot(),
                local_report_path=Path("ui_image_check_report.html"),
            ))
            return
        if parsed.path.startswith("/local/"):
            self._serve_local_file(parsed.path)
            return
        if parsed.path.startswith("/static/"):
            self._serve_app_static_file(parsed.path)
            return
        if parsed.path.startswith("/reports/runs/") and parsed.path.endswith("/api/log"):
            self._serve_run_log(parsed.path)
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
        if "check_config" in data:
            candidate.check_config = str(data["check_config"])
        if "ocr_workers" in data:
            try:
                candidate.ocr_workers = int(data["ocr_workers"])
            except (TypeError, ValueError) as exc:
                raise ValueError("ocr_workers must be an integer") from exc
        if "advanced_args" in data:
            raw_advanced = data["advanced_args"]
            if not isinstance(raw_advanced, dict):
                raise ValueError("advanced_args must be an object")
            candidate.advanced_args = dict(raw_advanced)
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
        self.config.check_config = candidate.check_config
        self.config.ocr_workers = candidate.ocr_workers
        self.config.advanced_args = candidate.advanced_args
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

    def _serve_local_file(self, request_path: str) -> None:
        relative = urllib.parse.unquote(request_path.removeprefix("/local/")).replace("\\", "/")
        static_root = self.static_root.resolve()
        target = (static_root / relative).resolve()
        if target == static_root or static_root not in target.parents or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix.lower() in {".html", ".htm"}:
            content_type = "text/html; charset=utf-8"
        self._send_bytes(target.read_bytes(), content_type)

    def _serve_app_static_file(self, request_path: str) -> None:
        relative = urllib.parse.unquote(request_path.removeprefix("/static/")).replace("\\", "/")
        static_root = self.app_static_root.resolve()
        target = (static_root / relative).resolve()
        if target == static_root or static_root not in target.parents or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        self._send_bytes(target.read_bytes(), content_type)

    def _serve_run_log(self, request_path: str) -> None:
        parts = urllib.parse.unquote(request_path).strip("/").split("/")
        if len(parts) != 5:
            self._send_json({"ok": False, "error": "invalid run log path"}, status=HTTPStatus.NOT_FOUND)
            return
        run_id = parts[2]
        reports_root = Path(self.config.reports_dir).resolve()
        target = (reports_root / "runs" / run_id / "run.log").resolve()
        if reports_root not in target.parents or not target.is_file():
            self._send_json({"ok": False, "error": "run log not found"}, status=HTTPStatus.NOT_FOUND)
            return
        text = target.read_text(encoding="utf-8", errors="replace")
        self._send_json({"ok": True, "run_id": run_id, "log": text[-20000:]})

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
    static_root: Path | None = None,
) -> ThreadingHTTPServer:
    class BoundHandler(ReportServiceHandler):
        pass

    BoundHandler.config = config
    BoundHandler.config_path = config_path
    BoundHandler.runner = runner
    BoundHandler.get_next_run_text = staticmethod(get_next_run_text)
    BoundHandler.static_root = (static_root or Path.cwd()).resolve()
    BoundHandler.app_static_root = (Path(__file__).resolve().parent / "static").resolve()
    return ThreadingHTTPServer((config.host, config.port), BoundHandler)
