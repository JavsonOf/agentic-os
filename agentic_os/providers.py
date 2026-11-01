"""Model providers configured at runtime (from the War Room UI or code).

Each provider has a kind (``anthropic``, ``gemini`` or ``openai_compat``), an
API key, an optional base URL and a default model. Keys are stored server-side
in a JSON file readable only by the owner, and are never returned in full.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import asdict, dataclass
from typing import Any

from agentic_os.llm.base import LLMError, LLMProvider
from agentic_os.net import same_site
from agentic_os.storage import read_json, write_json

KINDS = ("anthropic", "gemini", "openai_compat")

PRESETS: list[dict[str, str]] = [
    {"id": "anthropic", "label": "Anthropic (Claude)", "kind": "anthropic", "base_url": "", "default_model": "claude-opus-5-5"},
    {"id": "gemini", "label": "Google Gemini", "kind": "gemini", "base_url": "", "default_model": "gemini-flash-latest"},
    {"id": "openai", "label": "OpenAI", "kind": "openai_compat", "base_url": "https://api.openai.com/v1", "default_model": ""},
    {"id": "openrouter", "label": "OpenRouter", "kind": "openai_compat", "base_url": "https://openrouter.ai/api/v1", "default_model": "openrouter/free"},
    {"id": "xai", "label": "xAI (Grok)", "kind": "openai_compat", "base_url": "https://api.x.ai/v1", "default_model": ""},
    {"id": "groq", "label": "Groq", "kind": "openai_compat", "base_url": "https://api.groq.com/openai/v1", "default_model": ""},
    {"id": "deepseek", "label": "DeepSeek", "kind": "openai_compat", "base_url": "https://api.deepseek.com/v1", "default_model": ""},
    {"id": "mistral", "label": "Mistral", "kind": "openai_compat", "base_url": "https://api.mistral.ai/v1", "default_model": ""},
    {"id": "huggingface", "label": "Hugging Face", "kind": "openai_compat", "base_url": "https://router.huggingface.co/v1", "default_model": ""},
    {"id": "ollama", "label": "Ollama (lokalnie)", "kind": "openai_compat", "base_url": "http://localhost:11434/v1", "default_model": ""},
    {"id": "custom", "label": "Własny (zgodny z OpenAI)", "kind": "openai_compat", "base_url": "", "default_model": ""},
]

_ID = re.compile(r"[a-zA-Z0-9_-]{1,40}")


@dataclass
class ProviderConfig:
    id: str
    kind: str
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    label: str = ""
    daily_limit: int = 0  # requests per day the owner's plan allows (0 = not set), shown as a usage bar

    def public(self) -> dict[str, Any]:
        data = asdict(self)
        data["api_key"] = mask(self.api_key)
        data["has_key"] = bool(self.api_key)
        return data


def mask(key: str) -> str:
    """Hide a secret; long keys keep their last 4 characters so they can be told apart."""
    if not key:
        return ""
    return ("•" * 8) + key[-4:] if len(key) >= 16 else "•" * 8


def _same_endpoint(old: ProviderConfig, new: ProviderConfig) -> bool:
    if old.kind != new.kind:
        return False
    if not old.base_url or not new.base_url:
        return old.base_url == new.base_url
    return same_site(old.base_url, new.base_url)


class ProviderRegistry:
    """Thread-safe store of provider configs, optionally persisted to ``path``."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path
        self._lock = threading.Lock()
        self._items: dict[str, ProviderConfig] = {}
        for item in read_json(path, []):
            self._items[item["id"]] = ProviderConfig(**item)
        # requests made today and the last "Testuj" result per provider (no secrets, so a plain file)
        self._usage_path = os.path.join(os.path.dirname(os.path.abspath(path)), "usage.json") if path else None
        self._usage: dict[str, dict[str, Any]] = {}
        if self._usage_path and os.path.exists(self._usage_path):
            try:
                with open(self._usage_path, encoding="utf-8") as fh:
                    self._usage = json.load(fh)
            except (OSError, ValueError):
                self._usage = {}

    def _save_usage(self) -> None:
        if not self._usage_path:
            return
        tmp = f"{self._usage_path}.tmp{threading.get_ident()}"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self._usage, fh)
        os.replace(tmp, self._usage_path)

    def record_call(self, provider_id: str) -> None:
        today = time.strftime("%Y-%m-%d")
        with self._lock:
            entry = self._usage.setdefault(provider_id, {})
            if entry.get("date") != today:
                entry["date"], entry["count"] = today, 0
            entry["count"] = entry.get("count", 0) + 1
            self._save_usage()

    def record_test(self, provider_id: str, ok: bool) -> None:
        with self._lock:
            self._usage.setdefault(provider_id, {})["last_test"] = {"ok": ok, "at": time.time()}
            self._save_usage()

    def usage(self, provider_id: str) -> dict[str, Any]:
        entry = self._usage.get(provider_id, {})
        today = entry.get("count", 0) if entry.get("date") == time.strftime("%Y-%m-%d") else 0
        return {"today": today, "last_test": entry.get("last_test")}

    def _save(self) -> None:
        if not self.path:
            return
        write_json(self.path, [asdict(p) for p in self._items.values()])

    def upsert(self, config: ProviderConfig, keep_existing_key: bool = True) -> ProviderConfig:
        if not _ID.fullmatch(config.id):
            raise ValueError("Provider id must match [a-zA-Z0-9_-]{1,40}")
        if config.kind not in KINDS:
            raise ValueError(f"Provider kind must be one of {KINDS}")
        if config.kind == "openai_compat" and not config.base_url:
            raise ValueError("An OpenAI-compatible provider needs a base_url")
        if config.base_url and not re.match(r"https?://", config.base_url):
            raise ValueError("base_url must start with http:// or https://")
        with self._lock:
            existing = self._items.get(config.id)
            if keep_existing_key and existing and (not config.api_key or config.api_key.startswith("•")):
                if not _same_endpoint(existing, config):
                    # The stored key was issued for the old address: never send it somewhere new.
                    raise ValueError("Re-enter the API key when changing the provider address")
                config.api_key = existing.api_key  # editing other fields keeps the stored key
            self._items[config.id] = config
            self._save()
        return config

    def remove(self, provider_id: str) -> bool:
        with self._lock:
            found = self._items.pop(provider_id, None) is not None
            self._save()
        return found

    def get(self, provider_id: str) -> ProviderConfig:
        try:
            return self._items[provider_id]
        except KeyError:
            raise LLMError(f"No provider named {provider_id!r}") from None

    def ids(self) -> list[str]:
        return list(self._items)

    def public(self) -> list[dict[str, Any]]:
        return [{**p.public(), "usage": self.usage(p.id)} for p in self._items.values()]

    def build(self, provider_id: str, model: str | None = None) -> LLMProvider:
        """Instantiate an :class:`LLMProvider` for a stored config; its calls are counted per day."""
        llm = self._build(provider_id, model)
        complete = llm.complete

        def counted(*args: Any, **kwargs: Any) -> Any:
            self.record_call(provider_id)
            return complete(*args, **kwargs)

        llm.complete = counted  # type: ignore[method-assign]  # same object and type, calls are counted
        return llm

    def _build(self, provider_id: str, model: str | None = None) -> LLMProvider:
        cfg = self.get(provider_id)
        model = model or cfg.default_model
        if cfg.kind == "anthropic":
            try:
                import anthropic
            except ImportError as exc:  # pragma: no cover - depends on env
                raise LLMError("The 'anthropic' package is required: pip install -e \".[anthropic]\" in the agentic-os folder") from exc
            from agentic_os.llm.anthropic_provider import AnthropicProvider

            client = anthropic.Anthropic(api_key=cfg.api_key or None, base_url=cfg.base_url or None)
            # Server-side refusal fallbacks exist only on the Anthropic API itself.
            return AnthropicProvider(model or "claude-opus-5-5", client=client, fallbacks=not cfg.base_url)
        if cfg.kind == "gemini":
            from agentic_os.llm.gemini_provider import gemini_llm

            return gemini_llm(model or None, api_key=cfg.api_key or None)
        from agentic_os.llm.openai_compat import OpenAICompatProvider

        return OpenAICompatProvider(model or "", base_url=cfg.base_url, api_key=cfg.api_key or None)

    def models(self, provider_id: str) -> list[str]:
        """Model ids the provider currently offers to this key, so users pick a real one instead of guessing."""
        from agentic_os.llm.openai_compat import get_json

        cfg = self.get(provider_id)
        if cfg.kind == "anthropic":
            base = (cfg.base_url or "https://api.anthropic.com").rstrip("/")
            data = get_json(f"{base}/v1/models?limit=100", {"x-api-key": cfg.api_key, "anthropic-version": "2023-06-01"})
        else:
            if cfg.kind == "gemini":
                from agentic_os.llm.gemini_provider import GEMINI_OPENAI_BASE_URL as base
            else:
                base = cfg.base_url.rstrip("/")
            data = get_json(f"{base}/models", {"Authorization": f"Bearer {cfg.api_key}"} if cfg.api_key else {})
        ids = [str(m.get("id", "")).removeprefix("models/") for m in data.get("data", []) if isinstance(m, dict)]
        if cfg.kind == "gemini":  # the list also holds embedding, image and speech models that cannot chat
            ids = [i for i in ids if i.startswith("gemini") and not re.search(r"embed|image|tts|audio|live", i)]
        return sorted({i for i in ids if i})
