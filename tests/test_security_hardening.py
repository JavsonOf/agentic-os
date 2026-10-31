"""Regression tests for the critical and high findings of the repository audit."""

import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from agentic_os import AgenticOS, Settings, net
from agentic_os.memory.long_term import LongTermMemory
from agentic_os.memory.vector_store import VectorStore
from agentic_os.mods import Mod, ModRegistry
from agentic_os.providers import ProviderConfig, ProviderRegistry
from agentic_os.rag.pipeline import RAGPipeline
from agentic_os.server import make_server


def _serve(handler):
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def _post(base, path, headers):
    req = urllib.request.Request(base + path, method="POST", data=b"{}", headers={"Content-Type": "text/plain", **headers})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as err:
        return err.code


@pytest.fixture
def open_server():
    """A server without a password, as when it runs on the owner's own machine."""
    system = AgenticOS(Settings(provider="mock"))
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()
    system.shutdown()


def test_passwordless_server_refuses_other_sites_and_rebound_hosts(open_server):
    base = open_server
    # A page on another site posting to 127.0.0.1 (CSRF), e.g. to add an MCP server that runs a program.
    assert _post(base, "/mcp", {"Origin": "https://evil.example"}) == 403
    assert _post(base, "/mcp", {"Sec-Fetch-Site": "cross-site"}) == 403
    # A domain that resolves to 127.0.0.1 (DNS rebinding) cannot even read.
    req = urllib.request.Request(base + "/providers", headers={"Host": "evil.example"})
    with pytest.raises(urllib.error.HTTPError) as err:
        urllib.request.urlopen(req, timeout=10)
    assert err.value.code == 403
    # The War Room on localhost and local tools without an Origin keep working.
    port = base.rsplit(":", 1)[1]
    assert _post(base, "/memory", {"Origin": f"http://localhost:{port}"}) != 403
    with urllib.request.urlopen(base + "/providers", timeout=10) as resp:
        assert resp.status == 200


def test_concurrent_memory_writes_and_saves_do_not_crash(tmp_path):
    memory = LongTermMemory(path=str(tmp_path / "memory.json"))
    errors = []

    def write(n):
        try:
            for i in range(40):
                memory.remember(f"fakt {n}-{i}")
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=write, args=(n,)) for n in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert errors == []
    saved = json.loads((tmp_path / "memory.json").read_text(encoding="utf-8"))
    assert len(saved) == 240 and not list(tmp_path.glob(".vectors-*"))  # complete file, no temp leftovers
    assert len(VectorStore(path=str(tmp_path / "memory.json"))) == 240


def test_ingest_while_agents_retrieve_does_not_crash():
    rag = RAGPipeline()
    rag.add_document("Agentic OS przechowuje wiedzę w dokumentach. " * 20, source="start")
    errors, stop = [], threading.Event()

    def read():
        try:
            while not stop.is_set():
                rag.retrieve("wiedza dokumenty", k=3)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    readers = [threading.Thread(target=read) for _ in range(3)]
    for t in readers:
        t.start()
    for i in range(60):
        rag.add_document(f"Dokument numer {i} o wiedzy i agentach. " * 10, source=f"d{i}")
    stop.set()
    for t in readers:
        t.join()
    assert errors == []


def test_stored_keys_are_not_reused_for_a_new_address():
    providers = ProviderRegistry()
    providers.upsert(ProviderConfig("p", "openai_compat", api_key="sk-secret", base_url="https://api.openai.com/v1"))
    # Editing other fields at the same address keeps the key.
    kept = providers.upsert(ProviderConfig("p", "openai_compat", api_key="", base_url="https://api.openai.com/v2", label="x"))
    assert kept.api_key == "sk-secret"
    # Pointing the provider elsewhere without a new key must not carry the old one along.
    with pytest.raises(ValueError, match="Re-enter the API key"):
        providers.upsert(ProviderConfig("p", "openai_compat", api_key="••••cret", base_url="https://attacker.example/v1"))
    moved = providers.upsert(ProviderConfig("p", "openai_compat", api_key="sk-new", base_url="https://attacker.example/v1"))
    assert moved.api_key == "sk-new"

    mods = ModRegistry()
    mods.add(Mod("pogoda", "Pogoda", "https://api.weather.example/v1", headers={"X-Key": "secret"}))
    with pytest.raises(ValueError, match="Re-enter the mod's headers"):
        mods.add(Mod("pogoda", "Pogoda", "https://attacker.example/v1", headers={"X-Key": "••••cret"}))
    assert mods.add(Mod("pogoda", "Pogoda", "https://attacker.example/v1")).headers == {}


def test_credentials_never_follow_a_redirect_to_another_host():
    seen = []

    class Target(BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.headers.get("Authorization"))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    target, target_url = _serve(Target)

    class Origin(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(302)
            self.send_header("Location", target_url + "/steal" if self.path == "/away" else "/final")
            self.end_headers()

        def log_message(self, *a):
            pass

    origin, origin_url = _serve(Origin)
    try:
        req = urllib.request.Request(origin_url + "/away", headers={"Authorization": "Bearer sk-secret"})
        with pytest.raises(urllib.error.HTTPError, match="another host"):
            net.urlopen(req, timeout=10)
        assert seen == []  # the other host never got the request, let alone the key
        assert net.same_site("http://api.example/v1", "https://api.example/v2")
        assert not net.same_site("https://api.example/v1", "http://api.example/v1")
        assert not net.same_site("https://api.example", "https://api.example.evil.com")
    finally:
        for httpd in (origin, target):
            httpd.shutdown()
            httpd.server_close()
