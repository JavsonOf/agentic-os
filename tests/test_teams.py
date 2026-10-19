import json
import threading
import urllib.error
import urllib.request

import pytest

from agentic_os import AgenticOS, teams
from agentic_os.config import Settings
from agentic_os.server import make_server


def _request(base, method, path, body=None, token=None):
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


TOOLS = {"calculator", "csv_summary", "text_stats", "search_knowledge", "recall_memories", "remember_fact"}


def test_every_team_has_five_valid_skills():
    names = [s for t in teams.TEAMS for s in t.skills]
    assert len(teams.TEAMS) == 5 and len(names) == 25 and len(set(names)) == 25
    assert sorted(p.stem for p in teams.SKILLS_DIR.glob("*.md")) == sorted(names)  # no stray or missing files
    for name in names:
        skill = teams.load_skill(name)
        assert skill.name == name
        assert len(skill.description) > 20 and len(skill.instructions.splitlines()) >= 15
        assert set(skill.tools) <= TOOLS, f"{name} uses tools the OS does not have: {set(skill.tools) - TOOLS}"


def test_installing_a_team_adds_its_skills_and_agent_and_can_be_repeated():
    system = AgenticOS(Settings(provider="mock"))
    try:
        result = teams.install_team(system, "marketing")
        assert result["skills"] == list(teams.team("marketing").skills)
        assert system.describe("marketing")["skills"] == result["skills"]
        assert all(system.skills.get(s) for s in result["skills"])
        teams.install_team(system, "marketing")  # updating replaces, never duplicates
        assert sum(1 for s in system.skills.all() if s.name == "copywriting") == 1
        assert [t["installed"] for t in teams.public(system)] == [t.id == "marketing" for t in teams.TEAMS]
        with pytest.raises(KeyError):
            teams.install_team(system, "ghost")
    finally:
        system.shutdown()


def test_teams_http_api():
    system = AgenticOS(Settings(provider="mock", api_key="secret"))
    httpd = make_server(system, port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    try:
        status, data = _request(base, "GET", "/teams", token="secret")
        assert status == 200 and len(data["teams"]) == 5 and not any(t["installed"] for t in data["teams"])
        status, data = _request(base, "POST", "/teams/all/install", {}, "secret")
        assert status == 200 and [i["agent"] for i in data["installed"]] == [t.id for t in teams.TEAMS]
        assert all(t["installed"] for t in _request(base, "GET", "/teams", token="secret")[1]["teams"])
        assert _request(base, "POST", "/teams/ghost/install", {}, "secret")[0] == 404
    finally:
        httpd.shutdown()
        httpd.server_close()
        system.shutdown()
