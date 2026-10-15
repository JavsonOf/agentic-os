"""Release notes for GitHub releases, taken from CHANGELOG.md.

    python scripts/release_notes.py --tag android-9        notes of a release that has its own section
    python scripts/release_notes.py --since android-9      points added to "Następne wydanie" since that release

Sections are "## <tag> · <date>" for published releases and any other "## ..." heading (normally
"Następne wydanie") for changes that are not released yet. Points are grouped by "### <category>".
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CATEGORIES = ("Dodano", "Zmieniono", "Usunięto", "Naprawiono", "Ulepszono")
TAG_HEADING = re.compile(r"^##\s+(android-\d+)\b")
INSTALL = ("---\n**Instalacja na Androidzie:** otwórz tę stronę na telefonie, dotknij **AgenticOS.apk** i zezwól "
           "przeglądarce na instalację, gdy zapyta. Nowa wersja instaluje się na poprzedniej.")


def parse(text: str) -> list[tuple[str | None, str, str]]:
    """Return (tag or None, category, point) for every bullet point."""
    points, tag, category, in_section = [], None, "", False
    for line in text.splitlines():
        if line.startswith("## "):
            m = TAG_HEADING.match(line)
            tag, category, in_section = (m.group(1) if m else None), "", True
        elif line.startswith("### "):
            category = line[4:].strip()
        elif in_section and line.startswith("- ") and category:
            points.append((tag, category, line[2:].strip()))
    return points


def render(points: list[tuple[str, str]]) -> str:
    order = {c: i for i, c in enumerate(CATEGORIES)}
    groups: dict[str, list[str]] = {}
    for category, point in points:
        groups.setdefault(category, []).append(point)
    if not groups:
        return "Drobne poprawki i aktualizacje."
    parts = []
    for category in sorted(groups, key=lambda c: order.get(c, len(order))):
        parts.append(f"### {category}\n" + "\n".join(f"- {p}" for p in groups[category]))
    return "\n\n".join(parts)


def notes_for_tag(text: str, tag: str) -> str:
    return render([(c, p) for t, c, p in parse(text) if t == tag])


def notes_since(text: str, previous_text: str) -> str:
    """Unreleased points that were not there when the previous release was published."""
    old = {p for _, _, p in parse(previous_text)}
    return render([(c, p) for t, c, p in parse(text) if t is None and p not in old])


def file_at(ref: str, path: str = "CHANGELOG.md") -> str:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="release with its own section in CHANGELOG.md")
    group.add_argument("--since", help="previous release tag (empty for the first release)")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    args = parser.parse_args(argv)
    text = Path(args.changelog).read_text(encoding="utf-8")
    body = notes_for_tag(text, args.tag) if args.tag else notes_since(text, file_at(args.since) if args.since else "")
    sys.stdout.write(f"{body}\n\n{INSTALL}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
