"""Server features behind the version C screens: schedules, knowledge files, usage bar, live progress."""

import io
import json
import subprocess
import threading
import urllib.request
import zipfile
import zlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from agentic_os import AgenticOS, Settings
from agentic_os.llm import LLMResponse, ScriptedLLM
from agentic_os.llm.base import ToolCall
from agentic_os.providers import ProviderConfig, ProviderRegistry
from agentic_os.rag.extract import _pdf_text_builtin, extract_text
from agentic_os.schedules import Schedule, ScheduleStore
from agentic_os.server import make_server

STATIC = Path(__file__).resolve().parents[1] / "agentic_os" / "server" / "static"


def _req(base, method, path, body=None, raw=None, token="pw"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(base + path, method=method, data=data)
    req.add_header("Content-Type", "application/octet-stream" if raw is not None else "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


@pytest.fixture
def war_room(tmp_path):
    system = AgenticOS(Settings(provider="mock", api_key="pw", data_dir=str(tmp_path)))
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", system
    httpd.shutdown()
    httpd.server_close()
    system.shutdown()


def _docx(paragraphs):
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", f'<w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>')
    return buf.getvalue()


def _pdf(lines):
    content = "BT /F1 12 Tf 72 720 Td " + " T* ".join(f"({line}) Tj" for line in lines) + " ET"
    stream = zlib.compress(content.encode("latin-1"))
    return (b"%PDF-1.4\n1 0 obj\n<< /Length " + str(len(stream)).encode() + b" /Filter /FlateDecode >>\nstream\n"
            + stream + b"\nendstream\nendobj\ntrailer\n<<>>\n%%EOF")


# ------------------------------------------------------------- extraction
def test_extract_text_reads_txt_docx_and_pdf():
    assert extract_text("Zażółć gęślą jaźń".encode(), "notatka.md") == "Zażółć gęślą jaźń"
    assert extract_text("cennik".encode("cp1250"), "a.txt") == "cennik"
    assert extract_text(_docx(["Pierwszy akapit", "Drugi akapit"]), "plan.docx") == "Pierwszy akapit\nDrugi akapit"
    assert _pdf_text_builtin(_pdf(["Hello PDF", "Second line"])) == "Hello PDF\nSecond line"
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(b"\x00\x01", "photo.png")
    with pytest.raises(ValueError, match="DOCX file is damaged"):
        extract_text(b"PK not a zip", "x.docx")


def test_builtin_pdf_reader_ignores_image_streams():
    raw = b"%PDF-1.4\n1 0 obj\n<< /Filter /DCTDecode >>\nstream\n\xff\xd8BT (x) Tj ET\nendstream\nendobj"
    assert _pdf_text_builtin(raw) == ""


# -------------------------------------------------------------- knowledge
def test_knowledge_upload_search_and_delete(war_room, tmp_path):
    base, _ = war_room
    status, r = _req(base, "POST", "/knowledge/upload?filename=plan.docx", raw=_docx(["Spotkanie z klientem we wtorek o 10"]))
    assert status == 201 and r["chunks"] >= 1
    _, docs = _req(base, "GET", "/knowledge")
    doc = docs["documents"][0]
    assert doc["source"] == "plan.docx" and doc["type"] == "docx" and doc["added_at"]
    _, hits = _req(base, "GET", "/knowledge/search?q=spotkanie%20klient")
    assert hits["results"] and hits["results"][0]["source"] == "plan.docx"
    assert _req(base, "DELETE", f"/knowledge/{doc['id']}")[0] == 200
    assert _req(base, "GET", "/knowledge")[1]["documents"] == []
    assert _req(base, "DELETE", f"/knowledge/{doc['id']}")[0] == 404
    # the saved copy forgets it too, so it does not come back after a restart
    assert doc["id"] not in (tmp_path / "knowledge.jsonl").read_text()
    assert _req(base, "POST", "/knowledge/upload?filename=x.png", raw=b"\x89PNG")[0] == 400
    assert _req(base, "POST", "/knowledge/upload?filename=x.txt", raw=b"   ")[0] == 400


# -------------------------------------------------------------- schedules
def test_schedule_runs_once_a_day_in_the_owner_time_zone(tmp_path):
    store = ScheduleStore(str(tmp_path / "schedules.json"))
    before = datetime(2026, 10, 15, 5, 0, tzinfo=timezone.utc)  # 07:00 in Warsaw
    s = store.add(Schedule(task="Podsumuj dzień", time="7:30", tz="Europe/Warsaw"), now=before)
    assert s.time == "07:30" and s.title == "Podsumuj dzień"
    assert store.due(before) == []
    at = datetime(2026, 10, 15, 5, 31, tzinfo=timezone.utc)  # 07:31 in Warsaw
    assert [x.id for x in store.due(at)] == [s.id]
    store.mark_run(s.id, "pid1", at)
    assert store.due(at) == []
    assert ScheduleStore(str(tmp_path / "schedules.json")).get(s.id).last_pid == "pid1"
    # created after today's time: waits for tomorrow instead of firing at once
    late = store.add(Schedule(task="x", time="06:00", tz="Europe/Warsaw"), now=at)
    assert late not in store.due(at)
    weekend = store.add(Schedule(task="y", time="00:00", days="weekends"), now=datetime(2026, 10, 14, 0, 0, tzinfo=timezone.utc))
    assert weekend not in store.due(datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc))  # Thursday
    for bad in (Schedule(task=""), Schedule(task="x", time="25:00"), Schedule(task="x", days="monthly")):
        with pytest.raises(ValueError):
            store.add(bad)


def test_schedule_api_and_due_runs(war_room):
    base, system = war_room
    status, s = _req(base, "POST", "/schedules", {"task": "Napisz raport", "time": "07:30", "title": "Raport", "tz": "Europe/Warsaw"})
    assert status == 201 and s["enabled"] is True
    assert _req(base, "POST", f"/schedules/{s['id']}", {"enabled": False})[1]["enabled"] is False
    assert _req(base, "GET", "/schedules")[1]["schedules"][0]["title"] == "Raport"
    assert _req(base, "POST", "/schedules", {"task": "x", "agent": "nobody"})[0] == 404
    assert _req(base, "POST", "/schedules", {"task": "x", "time": "7"})[0] == 400
    _req(base, "POST", f"/schedules/{s['id']}", {"enabled": True})
    system.schedules.get(s["id"]).last_run = ""
    started = system.run_due_schedules(datetime(2026, 10, 15, 6, 0, tzinfo=timezone.utc))
    assert len(started) == 1 and system.schedules.get(s["id"]).last_pid == started[0].pid
    assert system.run_due_schedules(datetime(2026, 10, 15, 6, 5, tzinfo=timezone.utc)) == []
    status, proc = _req(base, "POST", f"/schedules/{s['id']}/run", {})
    assert status == 202 and proc["task"] == "Napisz raport"
    assert _req(base, "DELETE", f"/schedules/{s['id']}")[0] == 200
    assert _req(base, "DELETE", f"/schedules/{s['id']}")[0] == 404


# ------------------------------------------------- usage bar and progress
def test_provider_usage_counts_calls_and_remembers_the_test(tmp_path):
    reg = ProviderRegistry(str(tmp_path / "providers.json"))
    reg.upsert(ProviderConfig("local", "openai_compat", base_url="http://127.0.0.1:9/v1", daily_limit=20))
    reg.record_call("local")
    reg.record_call("local")
    reg.record_test("local", True)
    pub = ProviderRegistry(str(tmp_path / "providers.json")).public()[0]
    assert pub["daily_limit"] == 20 and pub["usage"]["today"] == 2 and pub["usage"]["last_test"]["ok"] is True
    assert "api_key" not in json.loads((tmp_path / "usage.json").read_text())["local"]


def test_daily_limit_is_kept_when_another_field_changes(war_room):
    base, _ = war_room
    _req(base, "POST", "/providers", {"id": "local", "kind": "openai_compat", "base_url": "http://127.0.0.1:9/v1", "daily_limit": "25"})
    _req(base, "POST", "/providers", {"id": "local", "kind": "openai_compat", "base_url": "http://127.0.0.1:9/v1", "default_model": "m2"})
    p = _req(base, "GET", "/providers")[1]["providers"][0]
    assert p["daily_limit"] == 25 and p["default_model"] == "m2"
    assert _req(base, "POST", "/providers", {"id": "local", "kind": "openai_compat", "base_url": "http://x/v1", "daily_limit": "dużo"})[0] == 400


def test_processes_report_live_steps_and_output_preview():
    llm = ScriptedLLM([LLMResponse(text="", tool_calls=[ToolCall("1", "calculator", {"expression": "2+2"})], stop_reason="tool_use"), "Wynik: 4"])
    system = AgenticOS(Settings(provider="mock"), llm=llm)
    proc = system.run("ile to 2+2?")
    assert proc.step == 2 and proc.max_steps == system.settings.max_steps
    row = system.ps()[0]
    assert row["output"] == "Wynik: 4" and "result" not in row
    system.shutdown()


def test_pending_approvals_say_how_long_they_wait():
    system = AgenticOS(Settings(provider="mock"))
    item = threading.Thread(target=system._wait_for_operator, args=("assistant", "zapisz", {}, "tool"), daemon=True)
    item.start()
    for _ in range(100):
        if system.pending_approvals():
            break
        threading.Event().wait(0.01)
    a = system.pending_approvals()[0]
    assert 290 < a["expires_in"] <= 300 and a["expires_at"] > a["created_at"]
    system.decide_approval(a["id"], approve=False)
    system.shutdown()


# ------------------------------------------------------------ static app
def test_qr_generator_output_is_a_valid_symbol_layout():
    script = (f"const QR = require({json.dumps(str(STATIC / 'qr.js'))}); const m = QR.encode('https://x.app.github.dev/#connect=pw');"
              "process.stdout.write(JSON.stringify({size: m.length, corner: m[0].slice(0, 7), svg: QR.svg('a').startsWith('<svg')}))")
    out = json.loads(subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout)
    assert out["size"] in (25, 29, 33) and out["corner"] == [True] * 7 and out["svg"]


def test_version_c_screens_have_every_mock_up_element():
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    for text in ("Z kim dziś pracujemy?", "Szybkie zadania", "Streść moje notatki", "Zaplanuj tydzień", "Zbierz zespół agentów",
                 "Importuj pamięć z ChatGPT", 'aria-label="Mów"', 'aria-label="Ustawienia agenta"', 'aria-label="Dodaj plik"',
                 "Zaplanuj", "Wszystkie", "W toku", "Zaplanowane", "Dostawca", "Szukaj w dokumentach…", "Dodaj pliki",
                 "PDF, TXT, MD, DOCX · do 60 MB", "Twoje dokumenty", "Importuj pamięć", "Kolor akcentu", "Uprawnienia",
                 "Tryb myślenia", "Powiadomienia o prośbach", "Wyloguj", "Połącz z Agentic OS", "Adres serwera",
                 "Skanuj kod QR z komputera", "Jak go uruchomić"):
        assert text in html, text
    js = (STATIC / "app.js").read_text(encoding="utf-8")
    for text in ("Czeka na Ciebie jeszcze", "Zezwól", "Zawsze", "Odmów", "Wybierz inny model", "Darmowy plan · dzisiaj", "działa"):
        assert text in js, text
