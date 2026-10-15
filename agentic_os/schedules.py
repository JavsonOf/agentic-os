"""Recurring tasks ("Zaplanowane" in the War Room).

A schedule runs one task for one agent at a fixed time of day, every day, on
weekdays or on weekends, in the owner's time zone (the server often runs in
UTC while the phone shows Polish time). :meth:`ScheduleStore.due` decides what should run
now; the kernel submits those tasks and a background thread checks every
half minute while the server runs.
"""

from __future__ import annotations

import json
import os
import re
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DAYS = ("daily", "weekdays", "weekends")
_TIME = re.compile(r"([01]?\d|2[0-3]):([0-5]\d)")


@dataclass
class Schedule:
    task: str
    time: str = "07:30"
    agent: str = "assistant"
    days: str = "daily"
    title: str = ""
    enabled: bool = True
    last_run: str = ""  # date (YYYY-MM-DD) of the last run, so a task runs at most once a day
    last_pid: str = ""
    tz: str = ""  # IANA time zone of the owner, e.g. Europe/Warsaw; empty = the server's local time
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:10])

    def validate(self) -> None:
        if not self.task.strip():
            raise ValueError("A schedule needs a 'task'")
        m = _TIME.fullmatch(self.time.strip())
        if not m:
            raise ValueError("'time' must look like HH:MM")
        self.time = f"{int(m.group(1)):02d}:{m.group(2)}"
        if self.days not in DAYS:
            raise ValueError(f"'days' must be one of {DAYS}")
        self.title = (self.title or self.task).strip()[:80]
        if self.tz:
            try:
                ZoneInfo(self.tz)
            except (ZoneInfoNotFoundError, ValueError):
                self.tz = ""  # unknown on this server: fall back to its local time

    def zone(self) -> tzinfo | None:
        try:
            return ZoneInfo(self.tz) if self.tz else None
        except (ZoneInfoNotFoundError, ValueError):
            return None

    def local(self, now: datetime) -> datetime:
        """``now`` (timezone-aware) as the wall-clock time this schedule is written in."""
        return now.astimezone(self.zone())

    def runs_on(self, now: datetime) -> bool:
        weekend = now.weekday() >= 5
        return self.days == "daily" or (self.days == "weekends") == weekend

    def is_due(self, now: datetime) -> bool:
        now = self.local(now)
        return (self.enabled and self.runs_on(now) and now.strftime("%H:%M") >= self.time
                and self.last_run != now.strftime("%Y-%m-%d"))


class ScheduleStore:
    """Thread-safe list of schedules, optionally persisted to ``path``."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._items: dict[str, Schedule] = {}
        if path and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for item in json.load(fh):
                    s = Schedule(**item)
                    self._items[s.id] = s

    def _save(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        tmp = f"{self.path}.{uuid.uuid4().hex[:8]}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump([asdict(s) for s in self._items.values()], fh)
        os.replace(tmp, self.path)

    def all(self) -> list[Schedule]:
        return sorted(self._items.values(), key=lambda s: s.time)

    def get(self, sid: str) -> Schedule:
        try:
            return self._items[sid]
        except KeyError:
            raise ValueError(f"No schedule {sid!r}") from None

    def add(self, schedule: Schedule, now: datetime | None = None) -> Schedule:
        schedule.validate()
        now = now or datetime.now(timezone.utc)
        if schedule.is_due(now):  # created after today's time: start tomorrow instead of firing at once
            schedule.last_run = schedule.local(now).strftime("%Y-%m-%d")
        with self._lock:
            self._items[schedule.id] = schedule
            self._save()
        return schedule

    def update(self, sid: str, changes: dict[str, Any]) -> Schedule:
        with self._lock:
            current = self.get(sid)
            data = asdict(current)
            for key in ("task", "time", "agent", "days", "title", "enabled", "tz"):
                if key in changes:
                    data[key] = bool(changes[key]) if key == "enabled" else str(changes[key])
            updated = Schedule(**data)
            updated.validate()
            self._items[sid] = updated
            self._save()
        return updated

    def remove(self, sid: str) -> bool:
        with self._lock:
            found = self._items.pop(sid, None) is not None
            self._save()
        return found

    def mark_run(self, sid: str, pid: str, now: datetime) -> None:
        with self._lock:
            s = self._items.get(sid)
            if s is not None:
                s.last_run, s.last_pid = s.local(now).strftime("%Y-%m-%d"), pid
                self._save()

    def due(self, now: datetime) -> list[Schedule]:
        return [s for s in self.all() if s.is_due(now)]
