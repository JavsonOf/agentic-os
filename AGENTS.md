# Instructions for AI coding assistants

This file is for AI assistants (OmGithub, Claude Code, Codex, Cursor and others) that build, run or change
Agentic OS for the owner. Follow it step by step. When something here conflicts with a guess, this file wins.

## What this project is

Agentic OS is a Python framework with a built-in web app, the **War Room** (`agentic_os/server/static`).
The War Room is served by `agentic-os serve` on one port. It has no separate frontend build and no database:
state is stored as JSON files in a data directory.

## Build and run

```bash
pip install -e ".[gemini]"          # add ",anthropic" for Claude: ".[anthropic,gemini]"
export AGENTIC_OS_API_KEY="<password chosen by the owner>"
export AGENTIC_OS_DATA_DIR="$HOME/agentic-os-data"   # without this, agents, keys and memory are lost on restart
agentic-os serve --host 0.0.0.0 --port 8000
```

- `AGENTIC_OS_API_KEY` is the War Room login password. It is **required** when listening on `0.0.0.0`:
  the server refuses to start without it. Use exactly the value the owner gives you. Never invent one, and
  never print it in logs or commit it.
- `AGENTIC_OS_DATA_DIR` must point to a folder that survives restarts. Create it if needed.
- Health check: `curl http://localhost:8000/health` returns `{"status":"ok"}`.
- The app is at `/`. Expose port 8000 with the hosting platform's public URL or preview and give the owner
  that URL.
- Python 3.10 or newer. The core has no dependencies. Extras: `gemini` (google-genai), `anthropic`, `dev`.

If installing `.[gemini]` fails (google-genai needs compiled dependencies on some platforms), run
`pip install -e .` instead. Gemini then works through its OpenAI-compatible endpoint. Recent versions do this
automatically. In older versions, add it in the War Room under 🔑 Modele → "Własny (zgodny z OpenAI)" with
base URL `https://generativelanguage.googleapis.com/v1beta/openai` and model `gemini-flash-latest`.

Docker works too:

```bash
docker build -t agentic-os .
docker run -d -p 8000:8000 -e AGENTIC_OS_API_KEY="<password>" -v agentic-data:/home/agent/data agentic-os
```

## Update to the latest version

When the owner says "update", "zaktualizuj" or "pull the latest version":

```bash
git pull origin main
pip install -e ".[gemini]"      # picks up new dependencies, if any
# then restart: stop the running `agentic-os serve` and start it again with the same environment variables
```

Keep the same `AGENTIC_OS_API_KEY` and `AGENTIC_OS_DATA_DIR` across restarts unless the owner asks to change
them. After the restart, check `/health` and report the URL.

## Model API keys

The owner adds model keys (Gemini, Claude, OpenRouter and others) **inside the War Room**, in the 🔑 Modele
tab. They are stored on the server in owner-only files under the data directory. Do not ask the owner to
paste keys into chat, do not put keys in environment files you commit, and never echo them.

## Changing the code

- Run the checks before you commit:
  ```bash
  pip install -e ".[dev]"
  pytest -q
  ruff check .
  ```
  Every test must pass. Never skip or delete tests to make them pass.
- The test suite is offline: it uses mock models (`ScriptedLLM`, `HeuristicLLM`) and never calls real APIs.
- The War Room UI is plain HTML, CSS and JS (no build step) and its text is in **Polish**. When you change it,
  bump `CACHE` in `agentic_os/server/static/sw.js` so phones load the new version.
- Make changes on a branch and open a pull request against `main`. Do not push straight to `main`.
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Describe every user-visible change in `CHANGELOG.md` under **Następne wydanie**, in Polish, in one of
  the categories Dodano, Zmieniono, Usunięto, Naprawiono, Ulepszono. Each of those makes the merge publish a
  new release. Put small things that are not worth a release of their own (typos, cosmetics, refactoring,
  docs) under "Drobne zmiany": they wait for the next real release. These lines become the GitHub release
  notes automatically, so keep them general: what changed for the user, never keys, passwords, addresses,
  internal paths or how a security problem could be exploited (say "Poprawiono bezpieczeństwo …" instead).

## Release versions and names

- Releases and their git tags use SemVer `vMAJOR.MINOR.PATCH` (now `v0.MINOR.PATCH`), numbered one after
  another. Never use workflow run numbers or PR numbers as release names or tags.
- MAJOR: breaking changes or the first stable release (`v1.0.0`). MINOR: new features, screens or
  integrations (points under "Dodano"). PATCH: fixes, improvements, CI/CD, refactoring and docs. Put CI and
  docs work under "Zmieniono" or "Drobne zmiany", not "Dodano", so it does not bump MINOR.
- Release title, in English because the repository is public: `vX.Y.Z – Short Title Case Summary`
  (e.g. `v0.2.1 – Clear Connection Errors in the Android App`), without "Agentic OS" or "Release". The notes
  stay in Polish. Write the title in the `Tytuł:` line of **Następne wydanie** in `CHANGELOG.md`.
- The version is computed automatically. Add `Wersja: major` or `Wersja: minor` only when that automatic
  bump is too small. For a test build add `alpha`, `beta` or `rc` to the same line (see below).
- Test builds: `Wersja: alpha`, `beta` or `rc` (or e.g. `Wersja: major rc`) publishes a GitHub pre-release
  such as `v0.3.0-beta.1`, `-beta.2` on the next merge, never marked "Latest". Remove the line to publish the
  stable release, which keeps the tested number (`v0.3.0`).
- Rebuilds of the same code (no app change, e.g. a re-run): `Wersja: build` publishes `v0.2.6+build.1` (SemVer
  build metadata, APK `AgenticOS_v0.2.6_build.1.apk`); the version number itself stays. A `> Uwaga: …` line
  under a release heading in `CHANGELOG.md` is shown as a note on that release.
- The android workflow computes the version and publishes the release; `release-notes` keeps older releases
  in line with `CHANGELOG.md`. The APK asset is named `AgenticOS_vX.Y.Z.apk`.

## Never

- Commit secrets: API keys, passwords, tokens or `.env` files.
- Start the server on a public interface without `AGENTIC_OS_API_KEY`.
- Give agents shell or file-system access on the host. The server holds every API key, so this would let a
  prompt injection steal them.
- Delete or overwrite the data directory without the owner asking.

## Where things are

| Path | What it is |
|---|---|
| `agentic_os/kernel.py` | The OS: agents, processes, permissions, approvals, persistence |
| `agentic_os/server/__init__.py` | HTTP API (all routes are listed at the top) |
| `agentic_os/server/static/` | War Room web app (Polish UI, PWA) |
| `agentic_os/providers.py` | Model providers configured from the War Room |
| `agentic_os/llm/` | Anthropic, Gemini and OpenAI-compatible clients, plus offline mocks |
| `agentic_os/mcp.py`, `mods.py`, `skills.py` | MCP servers, HTTP "mods" and skills |
| `deploy/` | One-paste Oracle Cloud setup (`ORACLE.md`) |
| `tests/` | Offline test suite |
