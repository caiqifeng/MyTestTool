from __future__ import annotations

import datetime as dt
import threading
import time
import traceback
from typing import Callable


def next_daily_run(daily_run_time: str, now: dt.datetime | None = None) -> dt.datetime:
    current = now or dt.datetime.now()
    hour, minute = [int(part) for part in daily_run_time.split(":")]
    candidate = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= current:
        candidate = candidate + dt.timedelta(days=1)
    return candidate


class DailyScheduler:
    def __init__(
        self,
        get_daily_run_time: Callable[[], str],
        run_scheduled: Callable[[], None],
        poll_seconds: float = 5.0,
        error_handler: Callable[[BaseException, str], None] | None = None,
        now_provider: Callable[[], dt.datetime] | None = None,
    ):
        self.get_daily_run_time = get_daily_run_time
        self.run_scheduled = run_scheduled
        self.poll_seconds = poll_seconds
        self.error_handler = error_handler
        self.now_provider = now_provider or dt.datetime.now
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._next_run: dt.datetime | None = None
        self._lock = threading.Lock()

    @property
    def next_run(self) -> dt.datetime | None:
        with self._lock:
            return self._next_run

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="report-service-scheduler")
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _set_next_run(self, value: dt.datetime) -> None:
        with self._lock:
            self._next_run = value

    def _handle_error(self, exc: BaseException) -> None:
        if self.error_handler is None:
            return
        try:
            self.error_handler(exc, traceback.format_exc())
        except Exception:
            pass

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._set_next_run(next_daily_run(self.get_daily_run_time(), self.now_provider()))
            while not self._stop.is_set():
                next_run = self.next_run
                if next_run is not None and self.now_provider() >= next_run:
                    try:
                        self.run_scheduled()
                    except Exception as exc:
                        self._handle_error(exc)
                    break
                self._stop.wait(self.poll_seconds)
