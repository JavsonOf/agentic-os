"""AUDIT.md 2.5 (CSRF to a local stdio MCP server) and 2.6 (negative Content-Length)."""

import http.client
import json
import shlex
import sys
import threading
import urllib.error
import urllib.request

from agentic_os import AgenticOS, Settings
from agentic_os.server import make_server


def _start(api_key=None, data_dir=None):
    system = AgenticOS(Settings(provider="mock", api_key=api_key, data_dir=data_dir))
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    port = httpd.server_address[1]
    return system, httpd, f"http://127.0.0.1:{port}", port


def _stop(system, httpd):
    httpd.shutdown()
    httpd.server_close()
    system.shutdown()


def _post(base, path, body, headers, token=None):
    data = body if isinstance(body, bytes) else json.dumps(body).encode()
    hdrs = dict(headers)
    if token:
        hdrs["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(base + path, data=data, method="POST", headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        raw = err.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {}
        return err.code, payload


def _stdio_body(marker):
    code = f"import pathlib; pathlib.Path({str(marker)!r}).write_text('spawned')"
    command = f"{sys.executable} -c {shlex.quote(code)}"
    return {"name": "x", "transport": "stdio", "command": command}


def _raw(port, method, path, headers, body=b""):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    conn.putrequest(method, path)
    for name, value in headers.items():
        conn.putheader(name, value)
    conn.endheaders()
    if body:
        conn.send(body)
    resp = conn.getresponse()
    status = resp.status
    resp.read()
    conn.close()
    return status


# ----------------------------------------------------------------- 2.5 CSRF
def test_text_plain_post_to_mcp_is_rejected_and_spawns_nothing(tmp_path):
    marker = tmp_path / "spawned"
    system, httpd, base, _port = _start(data_dir=str(tmp_path / "data"))
    try:
        status, _ = _post(base, "/mcp", _stdio_body(marker), {"Content-Type": "text/plain"})
        assert status == 415
        assert not marker.exists()
        assert "x" not in system.mcp
    finally:
        _stop(system, httpd)


def test_foreign_origin_cannot_register_stdio_mcp(tmp_path):
    marker = tmp_path / "spawned"
    system, httpd, base, port = _start(data_dir=str(tmp_path / "data"))
    try:
        headers = {"Content-Type": "application/json", "Origin": "https://evil.example"}
        status, _ = _post(base, "/mcp", _stdio_body(marker), headers)
        assert status == 403
        # Same host, different port, is still another origin (a page on 127.0.0.1:9).
        headers["Origin"] = "http://127.0.0.1:9"
        status, _ = _post(base, "/mcp", _stdio_body(marker), headers)
        assert status == 403
        # The scheme has to match too: https is not this plain HTTP server.
        headers["Origin"] = f"https://127.0.0.1:{port}"
        status, _ = _post(base, "/mcp", _stdio_body(marker), headers)
        assert status == 403
        assert not marker.exists()
        assert "x" not in system.mcp
    finally:
        _stop(system, httpd)


def test_same_origin_and_missing_origin_json_posts_still_work(tmp_path):
    system, httpd, base, port = _start(data_dir=str(tmp_path / "data"))
    try:
        ok = {"Content-Type": "application/json"}
        assert _post(base, "/chat/reset", {}, ok)[0] == 200
        assert _post(base, "/chat/reset", {}, {**ok, "Origin": f"http://127.0.0.1:{port}"})[0] == 200
        # A charset parameter does not change the media type.
        charset = {"Content-Type": "application/json; charset=utf-8", "Origin": f"http://127.0.0.1:{port}"}
        assert _post(base, "/chat/reset", {}, charset)[0] == 200
    finally:
        _stop(system, httpd)


def test_allowed_origins_env_permits_one_extra_browser_origin(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTIC_OS_ALLOWED_ORIGINS", "https://app.example:8443, http://localhost:5173")
    system, httpd, base, _port = _start(api_key="pw", data_dir=str(tmp_path / "data"))
    try:
        extra = {"Content-Type": "application/json", "Origin": "https://app.example:8443"}
        assert _post(base, "/chat/reset", {}, extra, token="pw")[0] == 200
        other = {"Content-Type": "application/json", "Origin": "https://other.example"}
        assert _post(base, "/chat/reset", {}, other, token="pw")[0] == 403
        # curl and the Android app send no Origin, with or without the password.
        assert _post(base, "/chat/reset", {}, {"Content-Type": "application/json"}, token="pw")[0] == 200
    finally:
        _stop(system, httpd)


def test_forwarded_https_origin_matches_the_public_host(tmp_path):
    system, httpd, base, _port = _start(api_key="pw", data_dir=str(tmp_path / "data"))
    try:
        headers = {
            "Content-Type": "application/json",
            "Host": "war.example",
            "X-Forwarded-Proto": "https",
            "Origin": "https://war.example",
        }
        assert _post(base, "/chat/reset", {}, headers, token="pw")[0] == 200
        headers["Origin"] = "http://war.example"
        assert _post(base, "/chat/reset", {}, headers, token="pw")[0] == 403
    finally:
        _stop(system, httpd)


def test_knowledge_upload_keeps_its_own_content_type(tmp_path):
    system, httpd, base, _port = _start(api_key="pw", data_dir=str(tmp_path / "data"))
    try:
        for ctype in ("application/octet-stream", "multipart/form-data; boundary=----x"):
            status, payload = _post(
                base, "/knowledge/upload?filename=notatka.txt", b"Spotkanie w poniedzialek",
                {"Content-Type": ctype}, token="pw",
            )
            assert status == 201 and payload["chunks"] >= 1
    finally:
        _stop(system, httpd)


# ------------------------------------------------------- 2.6 Content-Length
def test_negative_and_non_numeric_content_length_are_400(tmp_path):
    system, httpd, _base, port = _start(data_dir=str(tmp_path / "data"))
    try:
        for length in ("-1", "-5", "nope", "1.5"):
            assert _raw(port, "POST", "/chat/reset", {
                "Content-Type": "application/json", "Content-Length": length,
            }) == 400
            assert _raw(port, "POST", "/knowledge/upload?filename=a.txt", {
                "Content-Type": "application/octet-stream", "Content-Length": length,
            }) == 400
    finally:
        _stop(system, httpd)


def test_oversized_json_and_upload_are_413(tmp_path, monkeypatch):
    monkeypatch.setattr("agentic_os.server.MAX_BODY", 8)
    monkeypatch.setattr("agentic_os.server.MAX_UPLOAD", 8)
    system, httpd, _base, port = _start(data_dir=str(tmp_path / "data"))
    try:
        small = b'{"ok":1}'  # 8 bytes, at the limit
        assert _raw(port, "POST", "/chat/reset", {
            "Content-Type": "application/json", "Content-Length": str(len(small)),
        }, small) == 200
        big = b'{"ok":10}'  # 9 bytes
        assert _raw(port, "POST", "/chat/reset", {
            "Content-Type": "application/json", "Content-Length": str(len(big)),
        }, big) == 413
        assert _raw(port, "POST", "/knowledge/upload?filename=a.txt", {
            "Content-Type": "application/octet-stream", "Content-Length": "9",
        }, b"123456789") == 413
        assert _raw(port, "POST", "/memory/import?filename=a.txt", {
            "Content-Type": "application/octet-stream", "Content-Length": "9",
        }, b"123456789") == 413
    finally:
        _stop(system, httpd)
