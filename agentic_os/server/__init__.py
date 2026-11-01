"""HTTP API for deploying Agentic OS (roadmap stage 11).

Standard library only (``http.server``), so it deploys anywhere Python
runs. Put it behind a reverse proxy (TLS, rate limits) in production.

Endpoints (JSON in, JSON out):

=======  ================================  =========================================
GET      /health                           liveness probe
GET      /usage?period=today|week|month    requests and tokens per day and per provider
GET      /status                           OS summary
GET      /metrics                          counters and latency percentiles
GET      /agents                           registered agents
POST     /agents                           spawn ``{name, instructions?, tools?, tool_tags?, conversational?,
                                           mode?, permission?, delegates?}``
POST     /run                              ``{task, agent?, context?, async?}`` -> process
GET      /processes                        process table
GET      /processes/{pid}                  one process, with its result
POST     /processes/{pid}/feedback         ``{reward, comment?}``, reward in [-1, 1]
POST     /knowledge                        ``{text, metadata?}`` or ``{documents: [...]}``
GET      /knowledge/search?q=              best matching fragments
POST     /knowledge/upload?filename=       raw file (PDF, DOCX, TXT, MD, CSV, JSON; up to 60 MB) -> text in the knowledge base
DELETE   /knowledge/{doc_id}               remove a document
GET/POST /schedules                        recurring tasks ``{task, time: "HH:MM", agent?, days?, title?, enabled?}``
POST     /schedules/{id}                   change ``{enabled?, time?, task?, ...}``; DELETE removes it
POST     /schedules/{id}/run               run a scheduled task now
POST     /goal                             ``{goal, agents?}`` -> plan + result
GET      /traces/{trace_id}                spans for one agent run
GET      /                                 War Room web app (PWA)
GET      /providers                        configured model providers (keys masked) + presets
POST     /providers                        add/update ``{id, kind, api_key?, base_url?, default_model?}``
POST     /providers/{id}/test              send a tiny prompt to check the key works
GET      /providers/{id}/models            model ids the provider offers to this key
DELETE   /providers/{id}                   remove a provider
POST     /settings/default                 ``{provider, model?}`` OS default model
POST     /agents/external                  ``{name, protocol, url, api_key?, model?, description?}``
DELETE   /agents/{name}                    remove an agent
POST     /chat                             ``{message, agent?, session?, async?}`` multi-turn chat
POST     /chat/reset                       ``{agent?, session?}``
POST     /crew                             ``{task, agents, process?}`` run a crew (async)
GET      /knowledge                        ingested documents
GET      /graph                            knowledge/memory graph for the Brain view
GET/POST /skills, DELETE /skills/{name}    skills (``{name, description, instructions, tools}`` or ``{markdown}``)
GET      /teams                            ready-made agent teams (5 agents, 25 skills) and whether installed
POST     /teams/{id}/install               add a team's skills and agent (``all`` installs every team)
GET/POST /mods, DELETE /mods/{name}        custom HTTP tools
GET/POST /mcp, DELETE /mcp/{name}          MCP servers; POST /mcp/{name}/reconnect
POST     /memory/import?filename=&distill= raw export file (zip/json/txt, up to 60 MB) or JSON ``{text}``
GET      /approvals                        tool calls and agent questions waiting for the operator
POST     /approvals/{id}                   ``{approve: bool, remember?: bool}`` or ``{answer: str}`` for a question
DELETE   /agents/{name}/allowed            forget the tools approved with "always allow"
POST     /agents/{name}/settings           ``{permission?, mode?, skills?}`` change an agent at any time
=======  ================================  =========================================

Set ``AGENTIC_OS_API_KEY`` to require ``Authorization: Bearer <key>``. The
server refuses to listen on a public interface without it.
"""

from __future__ import annotations

import hmac
import json
import logging
import os
import re
import threading
import time
import urllib.parse
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from agentic_os import teams
from agentic_os.agents.external import AGENT_PRESETS, PROTOCOLS, ExternalAgentConfig
from agentic_os.kernel import AgenticOS, AgenticOSError
from agentic_os.llm.base import LLMError, Message
from agentic_os.mcp import MCPError, config_from_dict
from agentic_os.mods import mod_from_dict
from agentic_os.providers import PRESETS, ProviderConfig
from agentic_os.rag.extract import extract_text, file_type
from agentic_os.rag.pipeline import Document
from agentic_os.schedules import Schedule, as_bool
from agentic_os.skills import Skill, parse_skill_md

log = logging.getLogger("agentic_os.server")
MAX_BODY = 2 * 1024 * 1024
MAX_UPLOAD = 60 * 1024 * 1024
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/qr.js": ("qr.js", "application/javascript; charset=utf-8"),
    "/errors.js": ("errors.js", "application/javascript; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
    "/wake.html": ("wake.html", "text/html; charset=utf-8"),
    "/icon.svg": ("icon.svg", "image/svg+xml"),
    "/icon-192.png": ("icon-192.png", "image/png"),
    "/icon-512.png": ("icon-512.png", "image/png"),
}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}
_NAME = re.compile(r"[a-zA-Z0-9_-]{1,40}")


class HTTPError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def _require(body: dict[str, Any], key: str, kind: type = str) -> Any:
    value = body.get(key)
    if not isinstance(value, kind) or (kind is str and not value.strip()):
        raise HTTPError(400, f"'{key}' is required and must be a {kind.__name__}")
    return value


def _limit(value: Any) -> int:
    """A daily request limit from a form: empty means "not set"."""
    if value in (None, ""):
        return 0
    try:
        limit = int(value)
    except (TypeError, ValueError):
        raise HTTPError(400, "'daily_limit' must be a whole number") from None
    if limit < 0:
        raise HTTPError(400, "'daily_limit' must be a whole number")
    return limit


def _existing_limit(system: AgenticOS, provider_id: str) -> int:
    return next((p["daily_limit"] for p in system.providers.public() if p["id"] == provider_id), 0)


LOGIN_WINDOW = 300  # seconds
LOGIN_MAX_FAILURES = 20  # wrong passwords per address in that window before it has to wait


def make_handler(system: AgenticOS) -> type[BaseHTTPRequestHandler]:
    api_key = system.settings.api_key
    failures: dict[str, list[float]] = {}  # client address -> times of recent wrong passwords
    failures_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        server_version = "AgenticOS/0.1"

        def log_message(self, fmt: str, *args: Any) -> None:  # quieter default logging
            system.metrics.incr("http.requests")

        # ----------------------------------------------------------- helpers
        def _send(self, status: int, payload: Any) -> None:
            data = json.dumps(payload, default=str).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _content_length(self) -> int:
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                raise HTTPError(400, "Invalid Content-Length") from None
            if length < 0:  # a negative length would make read() take the whole stream, past every limit
                raise HTTPError(400, "Invalid Content-Length")
            return length

        def _body(self) -> dict[str, Any]:
            length = self._content_length()
            if length > MAX_BODY:
                raise HTTPError(413, "Request body too large")
            if not length:
                return {}
            try:
                body = json.loads(self.rfile.read(length))
            except json.JSONDecodeError as exc:
                raise HTTPError(400, f"Invalid JSON: {exc}") from exc
            if not isinstance(body, dict):
                raise HTTPError(400, "JSON body must be an object")
            return body

        def _guard_local(self, method: str) -> None:
            """Without a password the server only trusts its own machine.

            A web page can still reach 127.0.0.1 from the owner's browser: directly (CSRF, e.g. a form that
            adds an MCP server which runs a program) or through a domain that resolves to 127.0.0.1 (DNS
            rebinding). Requests must name a local host, and browser writes must come from a local page.
            """
            if api_key:
                return  # every request needs the bearer token, which another site cannot read or send
            host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
            if host and host not in LOCAL_HOSTS:
                raise HTTPError(403, "Forbidden host: without AGENTIC_OS_API_KEY only localhost is accepted")
            if method != "GET":
                origin = self.headers.get("Origin")
                origin_host = (urllib.parse.urlsplit(origin).hostname or "") if origin and origin != "null" else ""
                if (origin and origin_host.lower() not in LOCAL_HOSTS) or self.headers.get("Sec-Fetch-Site") == "cross-site":
                    raise HTTPError(403, "Cross-site request refused")

        def _authorize(self) -> None:
            path = self.path.split("?", 1)[0]
            if not api_key or path == "/health" or path in STATIC_FILES:
                return
            client = self.client_address[0]
            now = time.time()
            with failures_lock:
                recent = [t for t in failures.get(client, []) if now - t < LOGIN_WINDOW]
                failures[client] = recent
                if len(recent) >= LOGIN_MAX_FAILURES:  # slows password guessing to a crawl
                    raise HTTPError(429, "Too many wrong passwords, try again in a few minutes")
            header = self.headers.get("Authorization", "")
            token = header.removeprefix("Bearer ").strip()
            if not hmac.compare_digest(token.encode(), api_key.encode()):
                if token:  # a request with no password at all is not a guess
                    with failures_lock:
                        failures.setdefault(client, []).append(now)
                raise HTTPError(401, "Missing or invalid API key")

        def _static(self, path: str) -> bool:
            entry = STATIC_FILES.get(path)
            if entry is None:
                return False
            filename, ctype = entry
            with open(os.path.join(STATIC_DIR, filename), "rb") as fh:
                data = fh.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)
            return True

        def _dispatch(self, method: str) -> None:
            try:
                path = self.path.split("?", 1)[0]
                if method == "GET" and self._static(path):
                    return
                self._guard_local(method)
                self._authorize()
                status, payload = self._route(method, path.rstrip("/") or "/")
                self._send(status, payload)
            except HTTPError as exc:
                self._send(exc.status, {"error": exc.message})
            except AgenticOSError as exc:
                self._send(404, {"error": str(exc)})
            except (LLMError, MCPError, ValueError) as exc:
                self._send(400, {"error": str(exc)})
            except Exception as exc:
                system.metrics.incr("http.errors")
                log.exception("Unhandled error on %s %s", method, self.path.split("?", 1)[0])
                # The type and a short message help the owner; paths and long internals stay in the server log.
                self._send(500, {"error": f"{type(exc).__name__}: {str(exc).splitlines()[0][:200] if str(exc) else ''}"})

        def do_GET(self) -> None:
            self._dispatch("GET")

        def do_POST(self) -> None:
            self._dispatch("POST")

        def do_DELETE(self) -> None:
            self._dispatch("DELETE")

        # ------------------------------------------------------------ routes
        def _route(self, method: str, path: str) -> tuple[int, Any]:
            if method == "GET":
                if path == "/health":
                    return 200, {"status": "ok"}
                if path == "/usage":
                    period = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query).get("period", ["week"])[0]
                    days = {"today": 1, "week": 7, "month": 30}.get(period)
                    if days is None:
                        raise HTTPError(400, "period must be today, week or month")
                    return 200, {"period": period, **system.providers.history(days)}
                if path == "/status":
                    return 200, system.status()
                if path == "/metrics":
                    return 200, system.metrics.snapshot()
                if path == "/agents":
                    return 200, {"agents": [system.describe(n) for n in system.agents],
                                 "external_presets": AGENT_PRESETS, "tools": system.tools.names()}
                if path == "/providers":
                    return 200, {"providers": system.providers.public(), "presets": PRESETS,
                                 "default": {"provider": system.prefs.get("default_provider") or "env",
                                             "model": getattr(system.llm, "model", None),
                                             "name": getattr(system.llm, "name", None)}}
                if m := re.fullmatch(r"/providers/([\w-]+)/models", path):
                    return 200, {"models": system.providers.models(m.group(1))}
                if path == "/knowledge":
                    docs: dict[str, dict[str, Any]] = {}
                    for rec in system.knowledge.vectors.all():
                        doc_id = str(rec.metadata.get("doc_id"))
                        entry = docs.setdefault(doc_id, {"id": doc_id, "source": rec.metadata.get("source")
                                                         or rec.metadata.get("title") or "bez nazwy",
                                                         "type": rec.metadata.get("type") or "",
                                                         "added_at": rec.metadata.get("added_at"),
                                                         "chunks": 0, "preview": rec.text[:160]})
                        entry["chunks"] += 1
                    return 200, {"documents": list(docs.values())}
                if path == "/knowledge/search":
                    query = urllib.parse.parse_qs(self.path.partition("?")[2]).get("q", [""])[0].strip()
                    hits = system.knowledge.retrieve(query, k=8) if query else []
                    return 200, {"results": [{"doc_id": h.metadata.get("doc_id"), "source": h.source, "text": h.text[:400],
                                              "score": round(h.score, 4)} for h in hits]}
                if path == "/graph":
                    return 200, system.graph()
                if path == "/schedules":
                    return 200, {"schedules": [asdict(x) for x in system.schedules.all()]}
                if path == "/auth/check":
                    return 200, {"ok": True}
                if path == "/skills":
                    return 200, {"skills": system.skills.public()}
                if path == "/teams":
                    return 200, {"teams": teams.public(system)}
                if path == "/mods":
                    return 200, {"mods": [m.public() for m in system.mods.all()]}
                if path == "/mcp":
                    return 200, {"servers": [c.status() for c in system.mcp.values()]}
                if path == "/processes":
                    return 200, {"processes": system.ps()}
                if path == "/approvals":
                    return 200, {"approvals": system.pending_approvals()}
                if m := re.fullmatch(r"/processes/(\w+)", path):
                    return 200, system.process(m.group(1)).to_dict()
                if m := re.fullmatch(r"/traces/(\w+)", path):
                    return 200, {"spans": system.tracer.trace(m.group(1))}
                raise HTTPError(404, f"No route for GET {path}")

            if method == "DELETE":
                if m := re.fullmatch(r"/providers/([\w-]+)", path):
                    if not system.remove_provider(m.group(1)):
                        raise HTTPError(404, f"No provider {m.group(1)!r}")
                    return 200, {"ok": True}
                if m := re.fullmatch(r"/knowledge/([\w:-]+)", path):
                    if not system.remove_document(m.group(1)):
                        raise HTTPError(404, f"No document {m.group(1)!r}")
                    return 200, {"ok": True}
                if m := re.fullmatch(r"/schedules/(\w+)", path):
                    if not system.schedules.remove(m.group(1)):
                        raise HTTPError(404, f"No schedule {m.group(1)!r}")
                    return 200, {"ok": True}
                if m := re.fullmatch(r"/agents/([\w-]+)/allowed", path):
                    system.reset_always_allow(m.group(1))
                    return 200, {"ok": True}
                if m := re.fullmatch(r"/agents/([\w-]+)", path):
                    system.agent(m.group(1))
                    system.kill(m.group(1))
                    return 200, {"ok": True}
                removers = {"skills": system.remove_skill, "mods": system.remove_mod, "mcp": system.remove_mcp}
                if (m := re.fullmatch(r"/(skills|mods|mcp)/([\w-]+)", path)) and removers[m.group(1)](m.group(2)):
                    return 200, {"ok": True}
                raise HTTPError(404, f"No route or item for DELETE {path}")

            if path == "/knowledge/upload":
                query = urllib.parse.parse_qs(self.path.partition("?")[2])
                length = self._content_length()
                if length > MAX_UPLOAD:
                    raise HTTPError(413, "Plik jest za duży (max 60 MB)")
                raw = self.rfile.read(length) if length else b""
                filename = os.path.basename(query.get("filename", [""])[0]) or "plik.txt"
                if not raw.strip():
                    raise HTTPError(400, "Pusty plik")
                text = extract_text(raw, filename)
                if not text.strip():
                    raise HTTPError(400, "Pusty plik")
                doc = Document(text, {"source": filename, "type": file_type(filename) or "txt",
                                      "added_at": time.time(), "bytes": len(raw)})
                return 201, {"id": doc.id, "documents": 1, "chunks": system.ingest(doc)}

            if path == "/memory/import":
                query = urllib.parse.parse_qs(self.path.partition("?")[2])
                length = self._content_length()
                if length > MAX_UPLOAD:
                    raise HTTPError(413, "Plik jest za duży (max 60 MB)")
                raw = self.rfile.read(length) if length else b""
                filename = query.get("filename", [""])[0]
                distill = query.get("distill", ["0"])[0] in ("1", "true", "yes")
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    try:
                        payload = json.loads(raw or b"{}")
                    except json.JSONDecodeError as exc:
                        raise HTTPError(400, f"Invalid JSON: {exc}") from exc
                    if isinstance(payload, dict) and isinstance(payload.get("text"), str):
                        raw, filename = payload["text"].encode(), payload.get("filename") or "wklejone.txt"
                        distill = bool(payload.get("distill", distill))
                if not raw.strip():
                    raise HTTPError(400, "Pusty plik")
                return 200, system.import_memory(raw, filename, distill=distill)

            body = self._body()
            if m := re.fullmatch(r"/teams/([\w-]+)/install", path):
                ids = [t.id for t in teams.TEAMS] if m.group(1) == "all" else [m.group(1)]
                if any(i not in {t.id for t in teams.TEAMS} for i in ids):
                    raise HTTPError(404, f"No team {m.group(1)!r}")
                return 200, {"installed": [teams.install_team(system, i) for i in ids]}
            if path == "/skills":
                if isinstance(body.get("markdown"), str):
                    skill = parse_skill_md(body["markdown"], str(body.get("name") or ""))
                else:
                    tools = body.get("tools") or []
                    if isinstance(tools, str):
                        tools = [t.strip() for t in tools.split(",") if t.strip()]
                    skill = Skill(name=str(body.get("name", "")), description=str(body.get("description", "")),
                                  instructions=str(body.get("instructions", "")), tools=list(tools))
                return 201, system.add_skill(skill).__dict__
            if path == "/mods":
                return 201, system.add_mod(mod_from_dict(body)).public()
            if path == "/mcp":
                data = dict(body)
                if data.get("token"):
                    data.setdefault("headers", {})["Authorization"] = f"Bearer {data.pop('token')}"
                client = system.add_mcp(config_from_dict(data))
                return 201, client.status()
            if m := re.fullmatch(r"/mcp/([\w-]+)/reconnect", path):
                return 200, system.reconnect_mcp(m.group(1)).status()
            if path == "/providers":
                pid = _require(body, "id")
                cfg = ProviderConfig(
                    id=pid, kind=str(body.get("kind", "openai_compat")), api_key=str(body.get("api_key") or ""),
                    base_url=str(body.get("base_url") or ""), default_model=str(body.get("default_model") or ""),
                    label=str(body.get("label") or pid), daily_limit=_limit(body["daily_limit"]) if "daily_limit" in body
                    else _existing_limit(system, pid),
                )
                system.providers.upsert(cfg)
                if body.get("make_default"):
                    system.set_default_model(pid, cfg.default_model or None)
                return 201, cfg.public()
            if m := re.fullmatch(r"/providers/([\w-]+)/test", path):
                llm = system.providers.build(m.group(1), body.get("model") or None)
                try:
                    reply = llm.complete([Message.user("Reply with exactly: OK")], max_tokens=200)
                except Exception:
                    system.providers.record_test(m.group(1), False)
                    raise
                system.providers.record_test(m.group(1), True)
                return 200, {"ok": True, "reply": reply.text[:200], "model": reply.model or getattr(llm, "model", None)}
            if path == "/settings/default":
                system.set_default_model(_require(body, "provider"), body.get("model") or None)
                return 200, {"ok": True}
            if path == "/agents/external":
                name = _require(body, "name")
                if not _NAME.fullmatch(name):
                    raise HTTPError(400, "Agent name must match [a-zA-Z0-9_-]{1,40}")
                protocol = str(body.get("protocol", "openai"))
                if protocol not in PROTOCOLS:
                    raise HTTPError(400, f"protocol must be one of {PROTOCOLS}")
                agent = system.register_external(ExternalAgentConfig(
                    name=name, protocol=protocol, url=_require(body, "url"), api_key=str(body.get("api_key") or ""),
                    model=str(body.get("model") or ""), description=str(body.get("description") or ""),
                ))
                return 201, system.describe(agent.name)
            if path == "/chat":
                message = _require(body, "message")
                proc = system.chat(message, agent=str(body.get("agent") or "assistant"),
                                   session=str(body.get("session") or "default"), wait=not body.get("async", True))
                return (202 if body.get("async", True) else 200), proc.to_dict()
            if path == "/chat/reset":
                system.reset_chat(str(body.get("agent") or "assistant"), str(body.get("session") or "default"))
                return 200, {"ok": True}
            if path == "/crew":
                agents = body.get("agents")
                if not isinstance(agents, list) or not agents:
                    raise HTTPError(400, "'agents' must be a non-empty list")
                proc = system.submit_crew(_require(body, "task"), agents, str(body.get("process") or "manager"))
                return 202, proc.to_dict()
            if path == "/run":
                task = _require(body, "task")
                agent = body.get("agent", "assistant")
                context = body.get("context")
                if body.get("async"):
                    return 202, system.submit(task, agent=agent, context=context).to_dict()
                proc = system.run(task, agent=agent, context=context)
                return (200 if proc.status == "completed" else 500), proc.to_dict()
            if path == "/agents":
                name = _require(body, "name")
                if not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", name):
                    raise HTTPError(400, "Agent name must match [a-zA-Z0-9_-]{1,40}")
                kwargs: dict[str, Any] = {
                    "tools": body.get("tools"),
                    "tool_tags": body.get("tool_tags"),
                    "conversational": bool(body.get("conversational", False)),
                }
                if body.get("instructions"):
                    kwargs["instructions"] = str(body["instructions"])
                if isinstance(body.get("skills"), list):
                    kwargs["skills"] = [str(s) for s in body["skills"]]
                if body.get("provider") and body["provider"] != "default":
                    kwargs["provider"] = str(body["provider"])
                    kwargs["model"] = str(body.get("model") or "") or None
                kwargs["mode"] = str(body.get("mode") or "standard")
                kwargs["permission"] = str(body.get("permission") or ("ask" if body.get("approval") else "auto"))
                if isinstance(body.get("delegates"), list):
                    kwargs["delegates"] = [str(d) for d in body["delegates"]]
                agent = system.spawn(name, **kwargs)
                return 201, system.describe(agent.name)
            if m := re.fullmatch(r"/agents/([\w-]+)/settings", path):
                skills = body.get("skills")
                if skills is not None and (not isinstance(skills, list) or not all(isinstance(x, str) for x in skills)):
                    raise HTTPError(400, "'skills' must be a list of skill names")
                agent = system.update_agent(m.group(1), permission=body.get("permission") or None,
                                            mode=body.get("mode") or None, skills=skills)
                return 200, system.describe(agent.name)
            if m := re.fullmatch(r"/approvals/(\w+)", path):
                answer, approve = body.get("answer"), body.get("approve")
                if answer is not None:
                    if not isinstance(answer, str):
                        raise HTTPError(400, "'answer' must be text")
                    system.decide_approval(m.group(1), answer=answer)
                elif isinstance(approve, bool):
                    system.decide_approval(m.group(1), approve, remember=bool(body.get("remember", False)))
                else:
                    raise HTTPError(400, "Send 'approve' (true/false) or 'answer'")
                return 200, {"ok": True}
            if m := re.fullmatch(r"/processes/(\w+)/feedback", path):
                reward = body.get("reward")
                if not isinstance(reward, (int, float)) or not -1 <= reward <= 1:
                    raise HTTPError(400, "'reward' must be a number in [-1, 1]")
                system.give_feedback(m.group(1), float(reward), str(body.get("comment", "")))
                return 200, {"ok": True}
            if path == "/knowledge":
                docs = body.get("documents") or ([body] if body.get("text") else [])
                if not docs:
                    raise HTTPError(400, "Provide 'text' or 'documents'")
                chunks = 0
                for d in docs:
                    if not isinstance(d, dict) or not isinstance(d.get("text"), str):
                        raise HTTPError(400, "Each document needs a 'text' string")
                    meta = dict(d.get("metadata") or {})
                    meta.setdefault("added_at", time.time())
                    chunks += system.ingest(Document(d["text"], meta))
                return 201, {"documents": len(docs), "chunks": chunks}
            if path == "/schedules":
                sched = Schedule(task=str(body.get("task") or ""), time=str(body.get("time") or "07:30"),
                                 agent=str(body.get("agent") or "assistant"), days=str(body.get("days") or "daily"),
                                 title=str(body.get("title") or ""), enabled=as_bool(body.get("enabled", True)),
                                 tz=str(body.get("tz") or ""))
                return 201, asdict(system.add_schedule(sched))
            if m := re.fullmatch(r"/schedules/(\w+)/run", path):
                return 202, system.run_schedule(m.group(1)).to_dict()
            if m := re.fullmatch(r"/schedules/(\w+)", path):
                if "agent" in body:
                    system.agent(str(body["agent"]))
                return 200, asdict(system.schedules.update(m.group(1), body))
            if path == "/goal":
                result = system.goal(_require(body, "goal"), agents=body.get("agents"))
                return 200, result.to_dict()
            raise HTTPError(404, f"No route for POST {path}")

    return Handler


def make_server(system: AgenticOS, host: str = "127.0.0.1", port: int = 8000) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(system))


def serve(system: AgenticOS, host: str = "127.0.0.1", port: int = 8000) -> None:  # pragma: no cover - blocking
    if host not in ("127.0.0.1", "localhost", "::1") and not system.settings.api_key:
        raise SystemExit("Refusing to serve on a public interface without AGENTIC_OS_API_KEY (the War Room password).")
    httpd = make_server(system, host, port)
    system.start_scheduler()
    print(f"Agentic OS War Room on http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        system.shutdown(wait=False)
