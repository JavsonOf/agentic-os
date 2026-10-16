"""Bridge that lets Agentic OS hand tasks to OpenCode 2 (the "OpenCode" external agent, webhook protocol).

Agentic OS posts ``{"task", "context"}`` with ``Authorization: Bearer <token>``; the bridge runs
``opencode run "<task>"`` in a working folder and answers ``{"output": "..."}``. Standard library only, so it
runs anywhere Python 3.10+ does, e.g. in a Debian proot on Android (see docs/OPENCODE.md).

    python3 opencode_bridge.py --workdir ~/projekty/moj-projekt
    python3 opencode_bridge.py --port 8765 --model anthropic/claude-sonnet-4-5 --timeout 280

The token comes from OPENCODE_BRIDGE_TOKEN; without it a random one is generated and printed at start.
The bridge listens on 127.0.0.1 only unless --host says otherwise. OpenCode runs commands on this machine,
so expose the bridge to the internet only through a tunnel and never share the token.
"""

from __future__ import annotations

import argparse
import hmac
import json
import os
import re
import secrets
import shlex
import subprocess
import sys
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
MAX_BODY = 200_000  # bytes; a task is text, anything bigger is a mistake or abuse


@dataclass
class Settings:
    token: str
    workdir: Path
    command: list[str]
    model: str = ""
    timeout: float = 280.0  # below the 300 s Agentic OS waits for an external agent


def build_prompt(task: str, context: str | None) -> str:
    return f"{context.strip()}\n\n{task.strip()}" if context and context.strip() else task.strip()


def run_opencode(settings: Settings, prompt: str) -> str:
    args = [*settings.command, "run"]
    if settings.model:
        args += ["--model", settings.model]
    args.append(prompt)
    try:
        proc = subprocess.run(args, cwd=settings.workdir, capture_output=True, text=True,
                              timeout=settings.timeout, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Nie znaleziono programu {settings.command[0]!r}. Czy OpenCode jest zainstalowany?") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"OpenCode nie skończył w {settings.timeout:.0f} s. Podziel zadanie na mniejsze.") from exc
    output = ANSI.sub("", proc.stdout).strip()
    if proc.returncode != 0:
        detail = ANSI.sub("", proc.stderr).strip()[-500:] or output[-500:]
        raise RuntimeError(f"OpenCode zakończył się błędem (kod {proc.returncode}): {detail}")
    return output or "(OpenCode nie zwrócił żadnego tekstu)"


def make_handler(settings: Settings) -> type[BaseHTTPRequestHandler]:
    lock = threading.Lock()  # one OpenCode run at a time, so tasks do not edit the same files at once

    class Handler(BaseHTTPRequestHandler):
        server_version = "OpenCodeBridge/1"

        def _reply(self, status: int, data: dict) -> None:
            body = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # health check, no task and no secrets
            self._reply(200, {"ok": True, "busy": lock.locked()})

        def do_POST(self) -> None:
            sent = self.headers.get("Authorization", "")
            if not hmac.compare_digest(sent.encode(), f"Bearer {settings.token}".encode()):
                self._reply(401, {"error": "Zły albo brakujący token mostka."})
                return
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                self._reply(413 if length > MAX_BODY else 400, {"error": "Puste albo za duże zadanie."})
                return
            try:
                data = json.loads(self.rfile.read(length))
                task = data.get("task")
                context = data.get("context")
            except (json.JSONDecodeError, AttributeError):
                self._reply(400, {"error": "Oczekiwano JSON {\"task\": ..., \"context\": ...}."})
                return
            if not isinstance(task, str) or not task.strip():
                self._reply(400, {"error": "Brak treści zadania (task)."})
                return
            with lock:
                try:
                    output = run_opencode(settings, build_prompt(task, context if isinstance(context, str) else None))
                except RuntimeError as exc:
                    self._reply(502, {"error": str(exc)})
                    return
            self._reply(200, {"output": output})

        def log_message(self, fmt: str, *args: object) -> None:  # one short line per request, never the task text
            sys.stderr.write(f"[mostek] {self.address_string()} {fmt % args}\n")

    return Handler


def make_server(settings: Settings, host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(settings))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mostek Agentic OS → OpenCode 2 (protokół webhook)")
    parser.add_argument("--host", default="127.0.0.1", help="adres nasłuchu (domyślnie tylko ten telefon/komputer)")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--workdir", default="~/opencode-projekty", help="folder, w którym pracuje OpenCode")
    parser.add_argument("--model", default="", help="model OpenCode, np. anthropic/claude-sonnet-4-5")
    parser.add_argument("--timeout", type=float, default=280.0, help="limit czasu jednego zadania w sekundach")
    parser.add_argument("--command", default="opencode", help="jak uruchomić OpenCode (domyślnie: opencode)")
    args = parser.parse_args(argv)

    workdir = Path(args.workdir).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("OPENCODE_BRIDGE_TOKEN", "").strip()
    generated = not token
    token = token or secrets.token_urlsafe(24)
    settings = Settings(token=token, workdir=workdir, command=shlex.split(args.command), model=args.model,
                        timeout=args.timeout)
    server = make_server(settings, args.host, args.port)
    print(f"Mostek OpenCode działa: http://{args.host}:{server.server_address[1]}  (folder: {workdir})")
    if generated:
        print(f"Token (wpisz go w War Room jako klucz agenta OpenCode): {token}")
        print("Żeby token się nie zmieniał, ustaw go na stałe: export OPENCODE_BRIDGE_TOKEN=...")
    print("Zatrzymanie: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
