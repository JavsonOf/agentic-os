"""Regression tests for the medium and low findings of the repository audit."""

import io
import json
import threading
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone

import pytest

from agentic_os import AgenticOS, Settings, net
from agentic_os.llm import LLMError
from agentic_os.llm.openai_compat import OpenAICompatProvider
from agentic_os.mcp import child_env
from agentic_os.planning import Plan
from agentic_os.providers import ProviderConfig
from agentic_os.rag.extract import MAX_DOCX_XML, extract_text
from agentic_os.schedules import Schedule, ScheduleStore, as_bool
from agentic_os.server import make_server
from agentic_os.tools.builtin import calculator


def test_damaged_state_files_no_longer_stop_the_server(tmp_path):
    (tmp_path / "agents.json").write_text("[{\"name\": \"half", encoding="utf-8")
    (tmp_path / "knowledge.jsonl").write_text(
        json.dumps({"id": "d1", "text": "Pierwszy dokument o kotach.", "metadata": {}}) + "\n" + '{"id": "d2", "te',
        encoding="utf-8")
    system = AgenticOS(Settings(provider="mock", data_dir=str(tmp_path)))
    try:
        assert "assistant" in system.agents  # started with defaults
        assert system.knowledge.retrieve("koty", k=1)  # the complete line was kept, the cut one skipped
        assert list(tmp_path.glob("agents.json.corrupt-*"))  # the damaged file is kept for inspection
    finally:
        system.shutdown()


def test_removing_a_provider_keeps_its_agents(tmp_path):
    settings = Settings(provider="mock", data_dir=str(tmp_path))
    system = AgenticOS(settings)
    system.providers.upsert(ProviderConfig("p1", "openai_compat", api_key="k", base_url="https://api.example/v1",
                                           default_model="m"))
    system.spawn("writer", provider="p1")
    assert system.remove_provider("p1")
    assert "writer" in system.agents and system._specs["writer"]["provider"] is None
    system.shutdown()
    # A provider that disappears outside the app (e.g. a hand-edited file) does not delete the agent either.
    data = json.loads((tmp_path / "agents.json").read_text(encoding="utf-8"))
    for spec in data:
        if spec["name"] == "writer":
            spec["provider"] = "gone"
    (tmp_path / "agents.json").write_text(json.dumps(data), encoding="utf-8")
    again = AgenticOS(settings)
    try:
        assert "writer" in again.agents
    finally:
        again.shutdown()


def test_planner_survives_null_and_odd_fields():
    plan = Plan.from_dict({"tasks": [{"id": "a", "description": "Zbierz dane", "depends_on": None, "agent": ["x"]},
                                     42, {"id": "b", "description": "Napisz raport", "depends_on": "a"}]})
    assert [t.id for t in plan.tasks] == ["a", "b"] and plan.tasks[1].depends_on == ["a"]
    assert plan.tasks[0].agent is None


def test_openai_compat_adapts_the_output_length_parameter(monkeypatch):
    sent = []

    def fake(request, timeout=None):
        body = json.loads(request.data)
        sent.append({k: v for k, v in body.items() if "tokens" in k})
        if "max_tokens" in body and body["max_tokens"] > 8192:
            raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {},
                                         io.BytesIO(b'{"error": "max_tokens must be in [1, 8192]"}'))
        reply = {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}], "usage": {}}
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setattr(net, "urlopen", fake)
    llm = OpenAICompatProvider("deepseek-chat", base_url="https://api.deepseek.example/v1")
    assert llm.complete([]).text == "ok" and sent[-1] == {"max_tokens": 8192}
    assert llm.complete([]).text == "ok" and len(sent) == 3  # the cap is remembered: no second 400

    def newer(request, timeout=None):
        body = json.loads(request.data)
        if "max_tokens" in body:
            raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {}, io.BytesIO(
                b'{"error": "Unsupported parameter: max_tokens. Use max_completion_tokens instead."}'))
        reply = {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}], "usage": {}}
        return io.BytesIO(json.dumps(reply).encode())

    monkeypatch.setattr(net, "urlopen", newer)
    assert OpenAICompatProvider("o4-mini").complete([]).text == "ok"

    def reset(request, timeout=None):
        raise ConnectionResetError("reset by peer")

    monkeypatch.setattr(net, "urlopen", reset)
    with pytest.raises(LLMError, match="Connection to .* failed"):
        OpenAICompatProvider("m").complete([])


def test_schedules_do_not_fire_right_after_an_edit_and_parse_booleans():
    reg = ScheduleStore()
    now = datetime(2026, 10, 31, 12, 0, tzinfo=timezone.utc)
    s = reg.add(Schedule(task="raport", time="18:00", tz="UTC"), now=now)
    reg.update(s.id, {"time": "09:00"}, now=now)  # moved to a time that already passed today
    assert reg.due(now) == []
    off = reg.update(s.id, {"enabled": "false"}, now=now)
    assert off.enabled is False and as_bool("0") is False and as_bool("true") is True
    reg.update(s.id, {"enabled": True}, now=now)  # re-enabled after its time: starts tomorrow
    assert reg.due(now) == []


def test_calculator_refuses_numbers_that_would_exhaust_memory():
    assert str(calculator(expression="2**10")).endswith("1024")
    for bomb in ("((9**999)**999)**999", "(10**900)**999"):
        with pytest.raises(ValueError):
            calculator(expression=bomb)


def test_docx_that_unpacks_to_gigabytes_is_refused():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", b"<w:t>" + b"a" * (MAX_DOCX_XML + 10) + b"</w:t>")
    with pytest.raises(ValueError):
        extract_text(buf.getvalue(), "bomba.docx")


def test_server_rejects_negative_lengths_and_slows_down_password_guessing():
    system = AgenticOS(Settings(provider="mock", api_key="  secret\n"))  # stray whitespace is ignored
    assert system.settings.api_key == "secret"
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def call(path, token, headers=None, data=None):
        req = urllib.request.Request(base + path, data=data, method="POST" if data is not None else "GET",
                                     headers={"Authorization": f"Bearer {token}", **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status
        except urllib.error.HTTPError as err:
            return err.code

    try:
        import http.client

        conn = http.client.HTTPConnection("127.0.0.1", httpd.server_address[1], timeout=10)
        conn.putrequest("POST", "/memory")
        conn.putheader("Authorization", "Bearer secret")
        conn.putheader("Content-Length", "-5")
        conn.endheaders()
        assert conn.getresponse().status == 400
        conn.close()
        assert [call("/status", "wrong") for _ in range(20)] == [401] * 20
        assert call("/status", "wrong") == 429 and call("/status", "secret") == 429  # this address must wait
    finally:
        httpd.shutdown()
        httpd.server_close()
        system.shutdown()


def test_mcp_programs_do_not_inherit_server_secrets(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret")
    monkeypatch.setenv("AGENTIC_OS_API_KEY", "war-room")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_x")
    env = child_env()
    assert "PATH" in env and not {"ANTHROPIC_API_KEY", "AGENTIC_OS_API_KEY", "GITHUB_TOKEN"} & set(env)


def test_a_run_cut_at_the_step_limit_ends_with_an_assistant_message():
    from agentic_os import Agent
    from agentic_os.llm import LLMResponse, ScriptedLLM, ToolCall
    from agentic_os.tools import calculator as calc

    looping = [LLMResponse(text="", tool_calls=[ToolCall(f"c{i}", "calculator", {"expression": "1+1"})],
                           stop_reason="tool_use") for i in range(2)]
    agent = Agent("a", llm=ScriptedLLM(looping), tools=[calc], max_steps=2)
    result = agent.run("policz")
    assert result.stopped_reason == "max_steps" and result.messages[-1].role == "assistant"
