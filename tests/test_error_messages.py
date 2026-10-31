"""Every error Agentic OS can show must get a plain-Polish explanation in the War Room (static/errors.js)."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ERRORS_JS = Path(__file__).resolve().parent.parent / "agentic_os" / "server" / "static" / "errors.js"

# Raw messages as the server, the model providers (HTTP and SDKs) and MCP servers produce them,
# each with a fragment the Polish explanation must contain.
CASES = [
    ('Brak połączenia z serwerem', 'Brak połączenia'),
    ('Missing or invalid API key', 'hasło'),
    ('No route for GET /providers/x/models', 'starszą wersję'),
    ('Request body too large', 'za duży'),
    ('Invalid JSON: Expecting value', 'niepoprawne dane'),
    ('The \'google-genai\' package is required: pip install -e ".[gemini]" in the agentic-os folder', 'pip install'),
    ('A model id is required for an OpenAI-compatible provider', 'nazwy modelu'),
    ("No provider named 'gemini'", 'nie jest skonfigurowany'),
    ("No provider 'gemini'", 'nie jest skonfigurowany'),
    ('HTTP 400 from https://api.openai.com/v1/chat/completions: {"error": {"message": "This model\'s maximum context length is 128000 tokens"}}', 'za długa'),
    ("BadRequestError: Error code: 400 - {'error': {'type': 'invalid_request_error', 'message': 'Your credit balance is too low'}}", 'środków'),
    ('HTTP 429 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{"error": {"code": 429, "message": "You exceeded your current quota. Quota exceeded for metric: generate_content_free_tier_requests, limit: 20\\nPlease retry in 7h15m49.65s.", "status": "RESOURCE_EXHAUSTED"}}]', '7 h 16 min'),
    ("RateLimitError: Error code: 429 - {'type': 'error', 'error': {'type': 'rate_limit_error'}}", 'Za dużo zapytań'),
    ("ClientError: 429 RESOURCE_EXHAUSTED. {'error': {'details': [{'retryDelay': '40s'}]}}", 'Za dużo zapytań'),
    ('HTTP 404 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{"error": {"code": 404, "message": "This model models/gemini-2.5-flash is no longer available to new users.", "status": "NOT_FOUND"}}]', 'Wybierz model'),
    ('HTTP 404 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{"error": {"code": 404, "message": "models/gemini-x-lite is not found for API version v1main", "status": "NOT_FOUND"}}]', 'Wybierz model'),
    ("NotFoundError: Error code: 404 - {'type': 'error', 'error': {'type': 'not_found_error', 'message': 'model: claude-x'}}", 'Wybierz model'),
    ('HTTP 400 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{"error": {"message": "API key not valid. Please pass a valid API key.", "status": "INVALID_ARGUMENT"}}]', 'Klucz API'),
    ("AuthenticationError: Error code: 401 - {'type': 'error', 'error': {'type': 'authentication_error'}}", 'Klucz API'),
    ('HTTP 403 from https://x/v1/chat/completions: {"error": {"status": "PERMISSION_DENIED"}}', 'dostępu'),
    ('HTTP 503 from https://generativelanguage.googleapis.com/v1beta/openai/chat/completions: [{"error": {"code": 503, "message": "This model is currently experiencing high demand.", "status": "UNAVAILABLE"}}]', 'przeciążone'),
    ("OverloadedError: Error code: 529 - {'type': 'error', 'error': {'type': 'overloaded_error'}}", 'przeciążone'),
    ('Cannot reach https://api.groq.com/openai/v1/chat/completions: [Errno -2] Name or service not known', 'api.groq.com'),
    ('Non-JSON reply from https://example.com/v1/chat/completions: <html>', 'base_url'),
    ('HTTP 502 from https://openrouter.ai/api/v1/chat/completions: Bad Gateway', 'awarię'),
    ('HTTP 404 from https://openrouter.ai/api/v1/chat/completions: {"error":{"message":"0 endpoints out of 8 requested are available matching your guardrail restrictions and data policy. We removed them for the following reasons (an endpoint may have matched multiple reasons):\\nZDR violation (guardrail): 8 endpoints excluded; configurable at https://openrouter.ai/workspaces/default/guardrails","code":404}}', 'https://openrouter.ai/workspaces/default/guardrails'),
    ('HTTP 404 from https://openrouter.ai/api/v1/chat/completions: {"error":{"message":"No endpoints found matching your data policy (Free model publication). Configure: https://openrouter.ai/settings/privacy","code":404}}', 'ustawienia prywatności'),
    ('HTTP 404 from https://openrouter.ai/api/v1/chat/completions: {"error":{"message":"No endpoints found that support tool use. To learn more about provider routing, visit: https://openrouter.ai/docs/provider-routing","code":404}}', 'nie obsługuje narzędzi'),
    ('HTTP 400 from https://openrouter.ai/api/v1/chat/completions: {"error": {"message": "tools are not supported"}}', 'innego modelu'),
    ('TimeoutError: The read operation timed out', 'czasie'),
    ('Provider error: something odd', 'Dostawca modelu'),
    ("A2A error: {'code': -32000}", 'A2A'),
    ('Cannot reach webhook: [Errno 111] Connection refused', 'webhook'),
    ('The openai protocol needs a model id', 'nazwę modelu'),
    ('External agents have no permission or mode settings', 'Zewnętrzni'),
    ('Cannot reach MCP server: [Errno 111] Connection refused', 'MCP'),
    ('HTTP 401 from MCP server: unauthorized', 'token'),
    ('MCP server did not answer in time', 'na czas'),
    ('MCP process exited', 'nie działa'),
    ("Cannot start MCP command: [Errno 2] No such file or directory: 'npx'", 'zainstalowany'),
    ('MCP server sent no response', 'nie zwrócił'),
    ('MCP error -32601: Method not found', 'MCP'),
    ("No MCP server 'files'", 'nie istnieje'),
    ('A stdio MCP server needs a command', 'polecenie'),
    ("transport must be 'http' or 'stdio'", 'http albo stdio'),
    ("No agent named 'writer'. Running: ['assistant']", '„writer”'),
    ("No team 'ghost'", 'zespołu'),
    ("The default 'assistant' agent cannot be removed", 'nie można usunąć'),
    ("No process 'ab12cd34'", 'nie istnieje'),
    ("No pending approval 'x1' (it may have timed out)", 'wygasła'),
    ("Agent 'x' was created in code with a custom strategy and cannot be changed here", 'w kodzie'),
    ("'agents' must be a non-empty list", 'co najmniej jednego'),
    ('A crew needs at least one agent', 'co najmniej jednego'),
    ("process must be one of ('sequential', 'hierarchical')", 'sposób pracy'),
    ("mode must be one of ('standard', 'reflective', 'adaptive')", 'tryb'),
    ("permission must be one of ('ask', 'smart', 'auto', 'full')", 'uprawnień'),
    ("'reward' must be a number in [-1, 1]", '-1 do 1'),
    ("Send 'approve' (true/false) or 'answer'", 'Zezwól'),
    ("Plan has a dependency cycle among: ['a', 'b']", 'planu'),
    ('No JSON object found in model output', 'planu'),
    ('Missing prompt variable(s): topic', 'zmiennych'),
    ('Classifier is not trained', '👍'),
    ("'message' is required and must be a str", '„Wiadomość”'),
    ('Agent name must match [a-zA-Z0-9_-]{1,40}', 'maks. 40'),
    ('MCP server name must match [a-zA-Z0-9_-]{1,32}', 'maks. 32'),
    ('Provider id must match [a-zA-Z0-9_-]{1,40}', 'maks. 40'),
    ('base_url must start with http:// or https://', 'https://'),
    ('An OpenAI-compatible provider needs a base_url', 'adres API'),
    ("Provide 'text' or 'documents'", 'pusty'),
    ('Pusty plik', 'pusty'),
    ('A skill needs a description and instructions', 'opis i instrukcje'),
    ("Invalid parameter 'x' (type must be one of ['boolean', 'integer', 'number', 'string'])", 'typ'),
    ('Uszkodzony plik ZIP', 'ZIP'),
    ("KeyError: 'foo'", 'nieoczekiwany'),
    ('Forbidden host: without AGENTIC_OS_API_KEY only localhost is accepted', 'localhost'),
    ('Cross-site request refused', 'innej strony'),
    ('Re-enter the API key when changing the provider address', 'klucz API jeszcze raz'),
    ("Re-enter the mod's headers when changing its address", 'nagłówki'),
    ('HTTP Error 302: Refused a redirect to another host (evil.example) so the API key is not sent there', 'evil.example'),
]


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node.js to run the War Room's errors.js")
def test_every_known_error_has_a_polish_explanation():
    script = f"const {{ explainError }} = require({json.dumps(str(ERRORS_JS))});" \
             "process.stdout.write(JSON.stringify(JSON.parse(require('fs').readFileSync(0, 'utf8')).map(explainError)));"
    out = subprocess.run(["node", "-e", script], input=json.dumps([raw for raw, _ in CASES]),
                         capture_output=True, text=True, check=True).stdout
    for (raw, expected), hint in zip(CASES, json.loads(out)):
        assert hint, f"no explanation for: {raw}"
        assert expected in hint, f"{raw!r}\n  -> {hint!r}\n  (expected to contain {expected!r})"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node.js to run the War Room's errors.js")
def test_failed_task_prefix_does_not_change_the_explanation():
    # A failed agent run stores its error as "<ExceptionType>: <message>".
    script = f"const {{ explainError }} = require({json.dumps(str(ERRORS_JS))});" \
             "const raws = JSON.parse(require('fs').readFileSync(0, 'utf8'));" \
             "process.stdout.write(JSON.stringify(raws.map((r) => [explainError(r), explainError('LLMError: ' + r)])));"
    raws = [raw for raw, _ in CASES if not raw.startswith(("KeyError", "Brak połączenia"))]
    out = subprocess.run(["node", "-e", script], input=json.dumps(raws), capture_output=True, text=True, check=True).stdout
    for raw, (plain, prefixed) in zip(raws, json.loads(out)):
        assert plain == prefixed, f"{raw!r}: {plain!r} != {prefixed!r}"


@pytest.mark.skipif(shutil.which("node") is None, reason="needs Node.js to run the War Room's errors.js")
def test_unknown_text_is_left_alone():
    script = f"const {{ explainError }} = require({json.dumps(str(ERRORS_JS))});" \
             "process.stdout.write(JSON.stringify([explainError(''), explainError('Zapisano'), explainError(null)]));"
    out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [None, None, None]
