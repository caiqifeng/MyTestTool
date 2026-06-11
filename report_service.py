from __future__ import annotations

import argparse
import webbrowser
from pathlib import Path

from image_check_service.config import load_or_create_config, validate_config
from image_check_service.runner import ReportRunner
from image_check_service.scheduler import DailyScheduler
from image_check_service.web import create_server


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the i18n image check management service.")
    parser.add_argument("--config", default="report_service_config.json", help="service config JSON path")
    parser.add_argument("--no-browser", action="store_true", help="do not open the console in a browser")
    return parser.parse_args(argv)


def build_service_components(config_path: Path):
    config = load_or_create_config(config_path)
    errors = validate_config(config)
    if errors:
        raise ValueError("Service config has errors:\n" + "\n".join(f"- {error}" for error in errors))

    runner = ReportRunner(config)
    scheduler = DailyScheduler(
        get_daily_run_time=lambda: config.daily_run_time,
        run_scheduled=lambda: runner.run_once("scheduled"),
        is_enabled=lambda: config.schedule_enabled,
        get_weekdays=lambda: config.schedule_weekdays,
    )
    server = create_server(
        config,
        config_path,
        runner,
        get_next_run_text=lambda: scheduler.next_run.strftime("%Y-%m-%d %H:%M:%S") if scheduler.next_run else None,
    )
    config.port = int(server.server_address[1])
    return config, runner, scheduler, server


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config_path = Path(args.config)
    try:
        config, _runner, scheduler, server = build_service_components(config_path)
    except ValueError as exc:
        print(str(exc))
        return 2
    scheduler.start()
    url = f"http://{config.host}:{server.server_address[1]}/"
    print(f"Report service started: {url}")
    if not args.no_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping report service...")
    finally:
        scheduler.stop()
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
