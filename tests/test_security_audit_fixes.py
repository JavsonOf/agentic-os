"""Regression tests for the findings of the Cloudflare-method security audit (quick profile)."""

import io
import json
import socket
import threading
import time
import urllib.error
import urllib.request
import zipfile
from types import SimpleNamespace

import pytest

from agentic_os import AgenticOS, Settings
from agentic_os.agents.external import ExternalAgentConfig
from agentic_os.llm.base import ToolCall
from agentic_os.mcp import MCPClient, MCPError, MCPServerConfig
from agentic_os.memory import importer
from agentic_os.server import LOGIN_MAX_FAILURES, make_server


def _start(system):
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def _get(base, path, headers=None):
    req = urllib.request.Request(base + path, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, dict(resp.headers)
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers)


# ------------------------------------------------- login throttle behind a proxy
def test_wrong_passwords_behind_trusted_proxy_do_not_lock_out_the_owner(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTIC_OS_TRUSTED_PROXIES", "127.0.0.1")
    httpd, base = _start(AgenticOS(Settings(provider="mock", api_key="owner-pw", data_dir=str(tmp_path))))
    try:
        for i in range(LOGIN_MAX_FAILURES):
            assert _get(base, "/auth/check", {"Authorization": f"Bearer guess-{i}", "X-Forwarded-For": "203.0.113.7"})[0] == 401
        stranger = {"Authorization": "Bearer owner-pw", "X-Forwarded-For": "203.0.113.7"}
        owner = {"Authorization": "Bearer owner-pw", "X-Forwarded-For": "198.51.100.1"}
        assert _get(base, "/auth/check", stranger)[0] == 429  # the guesser is still throttled
        assert _get(base, "/auth/check", owner)[0] == 200  # but the owner gets in
    finally:
        httpd.shutdown()


def test_forwarded_header_from_untrusted_peer_is_ignored(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTIC_OS_TRUSTED_PROXIES", raising=False)
    httpd, base = _start(AgenticOS(Settings(provider="mock", api_key="owner-pw", data_dir=str(tmp_path))))
    try:
        for i in range(LOGIN_MAX_FAILURES):  # a guesser cannot dodge the limit by inventing addresses
            _get(base, "/auth/check", {"Authorization": f"Bearer guess-{i}", "X-Forwarded-For": f"10.0.0.{i}"})
        assert _get(base, "/auth/check", {"Authorization": "Bearer owner-pw"})[0] == 429
    finally:
        httpd.shutdown()


# ------------------------------------------------------- idle connections
def test_idle_connection_is_closed(tmp_path, monkeypatch):
    from agentic_os import server

    monkeypatch.setattr(server, "IDLE_TIMEOUT", 1)
    httpd, _base = _start(AgenticOS(Settings(provider="mock", data_dir=str(tmp_path))))
    try:
        sock = socket.create_connection(("127.0.0.1", httpd.server_address[1]))
        sock.settimeout(5)
        assert sock.recv(1) == b""  # the server hangs up instead of waiting forever
        sock.close()
    finally:
        httpd.shutdown()


def test_connection_cap_frees_slots(tmp_path, monkeypatch):
    from agentic_os import server

    monkeypatch.setattr(server, "IDLE_TIMEOUT", 1)
    monkeypatch.setattr(server, "MAX_CONNECTIONS", 3)
    httpd, base = _start(AgenticOS(Settings(provider="mock", data_dir=str(tmp_path))))
    try:
        idle = [socket.create_connection(("127.0.0.1", httpd.server_address[1])) for _ in range(5)]
        time.sleep(2)  # the idle ones time out and give their slots back
        assert _get(base, "/health")[0] == 200
        for s in idle:
            s.close()
    finally:
        httpd.shutdown()


# ------------------------------------------------------------- framing
def test_responses_forbid_framing(tmp_path):
    httpd, base = _start(AgenticOS(Settings(provider="mock", data_dir=str(tmp_path))))
    try:
        for path in ("/", "/health"):
            status, headers = _get(base, path)
            assert status == 200
            assert headers["X-Frame-Options"] == "DENY"
            assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]
    finally:
        httpd.shutdown()


# ------------------------------------------------------- nested zip bomb
def _zip(entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)
    return buf.getvalue()


def test_nested_archives_do_not_get_their_own_size_limit(monkeypatch):
    monkeypatch.setattr(importer, "MAX_UNZIPPED", 1_000_000)
    inner = _zip({"memories.txt": "- fact line abc\n" * 60_000})  # 960 kB, under the limit on its own
    outer = _zip({f"conv{i}.json": inner for i in range(40)})
    parsed = importer.parse_export(outer, "export.zip")
    assert parsed.facts == []  # nested archives are skipped, so nothing past the limit is unpacked


def test_plain_export_zip_still_imports():
    parsed = importer.parse_export(_zip({"memories.txt": "- likes tea\n- lives in Gdansk\n"}), "export.zip")
    assert len(parsed.facts) == 2


# --------------------------------------------- smart delegation to external
def test_smart_agent_asks_before_delegating_to_external_agent(tmp_path, monkeypatch):
    system = AgenticOS(Settings(provider="mock", data_dir=str(tmp_path)))
    system.register_external(ExternalAgentConfig(name="ext", protocol="webhook", url="http://127.0.0.1:9/hook"))
    system.spawn("helper")
    system.spawn("researcher", permission="smart", delegates=["ext", "helper"])
    asked = []
    monkeypatch.setattr(system, "_wait_for_operator",
                        lambda agent, tool, args, kind: asked.append(tool) or SimpleNamespace(decision=False))
    hook = system._approval_hook("researcher")
    assert hook(ToolCall("c1", "ask_helper", {"task": "x"})) is True  # native agent: own permissions
    assert hook(ToolCall("c2", "ask_ext", {"task": "x"})) is False  # external: waits for the operator
    assert asked == ["ask_ext"]


# ------------------------------------------------------ MCP name collisions
def _client(name, tool_names):
    client = MCPClient(MCPServerConfig(name, "http", "http://127.0.0.1:9/mcp"))
    client.tools = [{"name": n} for n in tool_names]
    return client


def test_mcp_tool_from_another_server_cannot_take_over_a_name(tmp_path):
    system = AgenticOS(Settings(provider="mock", data_dir=str(tmp_path)))
    system._register_mcp_tools(_client("files_admin", ["delete"]))
    with pytest.raises(MCPError):
        system._register_mcp_tools(_client("files", ["admin.delete"]))
    assert "mcp:files_admin" in system.tools._tools["mcp_files_admin_delete"].tags


def test_mcp_server_cannot_map_two_tools_to_one_name(tmp_path):
    system = AgenticOS(Settings(provider="mock", data_dir=str(tmp_path)))
    with pytest.raises(MCPError):
        system._register_mcp_tools(_client("files", ["a.b", "a_b"]))
    assert not [t for t in system.tools if t.name.startswith("mcp_")]


def test_mcp_server_can_reregister_its_own_tools(tmp_path):
    system = AgenticOS(Settings(provider="mock", data_dir=str(tmp_path)))
    system._register_mcp_tools(_client("files", ["read"]))
    system._register_mcp_tools(_client("files", ["read"]))  # a reconnect of the same server is fine
    assert json.dumps(sorted(system.tools._tools["mcp_files_read"].tags)) == '["mcp", "mcp:files"]'
