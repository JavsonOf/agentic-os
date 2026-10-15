"""Turn an uploaded file (TXT, MD, CSV, JSON, DOCX, PDF) into plain text for the knowledge base.

Standard library only. PDFs use ``pypdf`` when it is installed
(``pip install -e ".[pdf]"``) and otherwise a small built-in reader that
handles ordinary text PDFs; scanned PDFs (images only) have no text to read.
"""

from __future__ import annotations

import io
import os
import re
import zipfile
import zlib
from xml.etree import ElementTree

TEXT_TYPES = {"txt", "md", "markdown", "csv", "json", "log", "html", "htm", "xml", "yaml", "yml"}
SUPPORTED = sorted(TEXT_TYPES | {"pdf", "docx"})


def file_type(filename: str) -> str:
    return os.path.splitext(filename or "")[1].lower().lstrip(".")


def decode_text(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")  # pragma: no cover - latin-1 never fails


def extract_text(raw: bytes, filename: str) -> str:
    """Return the readable text of a file. Raises ``ValueError`` for unsupported or unreadable files."""
    kind = file_type(filename)
    if kind in TEXT_TYPES or (not kind and not raw.startswith((b"%PDF", b"PK"))):
        return decode_text(raw)
    if kind == "docx" or (not kind and raw.startswith(b"PK")):
        return _docx_text(raw)
    if kind == "pdf" or raw.startswith(b"%PDF"):
        return _pdf_text(raw)
    raise ValueError(f"Unsupported file type: .{kind} (supported: {', '.join(SUPPORTED)})")


def _docx_text(raw: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            xml = zf.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ValueError("This DOCX file is damaged or is not a Word document") from exc
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    root = ElementTree.fromstring(xml)
    paragraphs = []
    for p in root.iter(f"{ns}p"):
        parts = []
        for node in p.iter():
            if node.tag == f"{ns}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{ns}tab":
                parts.append("\t")
            elif node.tag in (f"{ns}br", f"{ns}cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs).strip()


def _pdf_text(raw: bytes) -> str:
    text = ""
    try:
        import pypdf  # optional, much better with unusual fonts

        reader = pypdf.PdfReader(io.BytesIO(raw))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
    except ImportError:
        text = _pdf_text_builtin(raw)
    except Exception as exc:
        raise ValueError(f"This PDF cannot be read: {exc}") from exc
    if not text.strip():
        raise ValueError("No readable text in this PDF (it may be a scan or use unusual fonts; "
                         "install pypdf for better PDF support)")
    return text.strip()


_STREAM = re.compile(rb"<<(.*?)>>\s*stream\r?\n(.*?)\r?\nendstream", re.DOTALL)
_TOKEN = re.compile(rb"\((?:\\.|[^\\)])*\)|\[[^\]]*\]|T[Jj*dD]|'|\"|ET|BT")
_STRING = re.compile(rb"\((?:\\.|[^\\)])*\)")
_ESCAPES = {b"n": b"\n", b"r": b"\r", b"t": b"\t", b"b": b"\b", b"f": b"\f", b"(": b"(", b")": b")", b"\\": b"\\"}


def _unescape(s: bytes) -> bytes:
    out, i = bytearray(), 0
    while i < len(s):
        c = s[i:i + 1]
        if c != b"\\":
            out += c
            i += 1
            continue
        nxt = s[i + 1:i + 2]
        if nxt in _ESCAPES:
            out += _ESCAPES[nxt]
            i += 2
        elif nxt.isdigit():
            octal = re.match(rb"[0-7]{1,3}", s[i + 1:i + 4]).group()  # type: ignore[union-attr]
            out.append(int(octal, 8) & 0xFF)
            i += 1 + len(octal)
        else:  # line continuation or unknown escape
            i += 2
    return bytes(out)


def _pdf_text_builtin(raw: bytes) -> str:
    """Read text-showing operators (Tj, TJ, ', ") from the page content streams."""
    lines: list[str] = []
    for header, data in _STREAM.findall(raw):
        if b"FlateDecode" in header:
            try:
                data = zlib.decompress(data)
            except zlib.error:
                continue
        elif b"/Filter" in header:
            continue  # images and other encodings carry no text
        if b"BT" not in data:
            continue
        current: list[str] = []
        for tok in _TOKEN.findall(data):
            if tok.startswith(b"("):
                current.append(_unescape(tok[1:-1]).decode("cp1252", errors="replace"))
            elif tok.startswith(b"["):
                for part in _STRING.findall(tok):
                    current.append(_unescape(part[1:-1]).decode("cp1252", errors="replace"))
            elif tok in (b"T*", b"Td", b"TD", b"'", b'"', b"ET") and current:
                lines.append("".join(current))
                current = []
        if current:
            lines.append("".join(current))
    return "\n".join(line for line in lines if line.strip())
