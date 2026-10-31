"""An in-memory vector database with optional JSON persistence."""

from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from agentic_os.memory.embeddings import Embedder, HashingEmbedder, cosine


@dataclass
class Record:
    id: str
    text: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchHit:
    record: Record
    score: float


class VectorStore:
    """Stores text with embeddings; brute-force cosine search.

    Fine for thousands of records. Swap in FAISS/pgvector/etc. behind the
    same methods for larger corpora. Thread-safe: agents, the server and uploads
    read and write the same store at once.
    """

    def __init__(self, embedder: Embedder | None = None, path: str | None = None) -> None:
        self.embedder = embedder or HashingEmbedder()
        self.path = path
        self._records: dict[str, Record] = {}
        self._lock = threading.RLock()
        if path and os.path.exists(path):
            self.load(path)

    def __len__(self) -> int:
        return len(self._records)

    def add(self, text: str, metadata: dict[str, Any] | None = None, id: str | None = None) -> str:
        rid = id or uuid.uuid4().hex[:12]
        record = Record(rid, text, self.embedder.embed(text), dict(metadata or {}))
        with self._lock:
            self._records[rid] = record
        return rid

    def get(self, rid: str) -> Record | None:
        with self._lock:
            return self._records.get(rid)

    def delete(self, rid: str) -> bool:
        with self._lock:
            return self._records.pop(rid, None) is not None

    def all(self) -> list[Record]:
        with self._lock:
            return list(self._records.values())

    def search(
        self,
        query: str,
        k: int = 5,
        where: dict[str, Any] | None = None,
        min_score: float = 0.0,
    ) -> list[SearchHit]:
        qv = self.embedder.embed(query)
        hits = []
        for rec in self.all():
            if where and any(rec.metadata.get(key) != val for key, val in where.items()):
                continue
            score = cosine(qv, rec.vector)
            if score >= min_score:
                hits.append(SearchHit(rec, score))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]

    def save(self, path: str | None = None) -> None:
        path = path or self.path
        if not path:
            raise ValueError("No path given for VectorStore.save")
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)
        with self._lock:  # one writer at a time; readers keep working on their snapshots
            data = [asdict(r) for r in self._records.values()]
            # Write a temp file and swap it in, so a crash mid-write never leaves a truncated store.
            fd, tmp = tempfile.mkstemp(dir=folder, prefix=".vectors-", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as fh:
                    json.dump(data, fh)
                os.replace(tmp, path)
            except BaseException:
                if os.path.exists(tmp):
                    os.unlink(tmp)
                raise

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as fh:
            items = json.load(fh)
        with self._lock:
            for item in items:
                rec = Record(**item)
                self._records[rec.id] = rec
