import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from agentic_os.agents.external import ExternalAgent, ExternalAgentConfig
from agentic_os.llm.base import LLMError

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("opencode_bridge", ROOT / "scripts" / "opencode_bridge.py")
bridge = importlib.util.module_from_spec(spec)
sys.modules["opencode_bridge"] = bridge  # dataclasses look the module up
spec.loader.exec_module(bridge)

TOKEN = "test-token"
FAKE_OPENCODE = """import sys
args = sys.argv[1:]
assert args[0] == "run", args
prompt = args[-1]
if "fail" in prompt:
    print("model error", file=sys.stderr)
    sys.exit(3)
print("\\x1b[32mZrobione:\\x1b[0m " + prompt)
"""


@pytest.fixture
def server(tmp_path):
    fake = tmp_path / "fake_opencode.py"
    fake.write_text(FAKE_OPENCODE, encoding="utf-8")
    settings = bridge.Settings(token=TOKEN, workdir=tmp_path, command=[sys.executable, str(fake)], timeout=20)
    srv = bridge.make_server(settings, "127.0.0.1", 0)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def post(url, data, token=TOKEN):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def test_bridge_runs_opencode_and_returns_its_output_without_colors(server):
    status, data = post(server, {"task": "Napraw test", "context": "Projekt w Pythonie"})
    assert status == 200
    assert data["output"] == "Zrobione: Projekt w Pythonie\n\nNapraw test"


def test_bridge_rejects_a_missing_or_wrong_token_and_empty_tasks(server):
    assert post(server, {"task": "x"}, token="")[0] == 401
    assert post(server, {"task": "x"}, token="wrong")[0] == 401
    assert post(server, {"task": "  "})[0] == 400


def test_bridge_reports_opencode_errors_in_plain_polish(server):
    status, data = post(server, {"task": "please fail"})
    assert status == 502 and "kod 3" in data["error"] and "model error" in data["error"]


def test_agentic_os_external_agent_talks_to_the_bridge(server):
    agent = ExternalAgent(ExternalAgentConfig(name="opencode", protocol="webhook", url=server, api_key=TOKEN))
    assert agent.run("Dodaj README").output == "Zrobione: Dodaj README"
    wrong = ExternalAgent(ExternalAgentConfig(name="opencode", protocol="webhook", url=server, api_key="nope"))
    with pytest.raises(LLMError):
        wrong._call_webhook("x", None)
