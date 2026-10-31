"""Safe JSON files for the server's state (agents, providers, skills, mods, schedules, memory).

Writes go to a private temp file that is swapped in with ``os.replace``, so a crash or a concurrent
reader never sees half a file. Reads are tolerant: a damaged file is set aside as ``<name>.corrupt-<time>``
and the server starts with the default instead of refusing to start.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import time
from typing import Any

log = logging.getLogger("agentic_os.storage")


def write_json(path: str, data: Any) -> None:
    """Atomically write ``data`` as JSON to ``path`` with owner-only permissions (files may hold API keys)."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=folder, prefix=f".{os.path.basename(path)}.", suffix=".tmp")  # mode 0o600
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def set_aside(path: str) -> str:
    """Rename a damaged file so it is kept for inspection but no longer blocks startup."""
    target = f"{path}.corrupt-{time.strftime('%Y%m%d-%H%M%S')}"
    os.replace(path, target)
    log.warning("Damaged file %s was set aside as %s", path, target)
    return target


def read_json(path: str | None, default: Any) -> Any:
    """Load JSON from ``path``; a missing file gives ``default``, a damaged one is set aside first."""
    if not path or not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, UnicodeDecodeError):
        set_aside(path)
        return default


def read_jsonl(path: str | None) -> list[Any]:
    """Load one JSON value per line, skipping (and logging) lines a crash left unfinished."""
    if not path or not os.path.exists(path):
        return []
    items = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        for number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                items.append(json.loads(line))
            except ValueError:
                log.warning("Skipped damaged line %d in %s", number, path)
    return items


__all__ = ["read_json", "read_jsonl", "set_aside", "write_json"]
