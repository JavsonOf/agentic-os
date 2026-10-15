"""Release versions, titles and notes for GitHub releases, taken from CHANGELOG.md.

Releases follow SemVer: tag ``vMAJOR.MINOR.PATCH`` (now ``v0.MINOR.PATCH``) and title
``vX.Y.Z – Short English Title``. See "Wersje i nazwy wydań" in CHANGELOG.md.

    python scripts/release_notes.py --tag v0.2.1             notes of a published release
    python scripts/release_notes.py --title v0.2.1           title of a published release
    python scripts/release_notes.py --since v0.2.4           points added to "Następne wydanie" since that release
    python scripts/release_notes.py --worth-release v0.2.4   "yes" if those points deserve their own release
    python scripts/release_notes.py --next-version v0.2.4    version of the next release, e.g. v0.2.5
    python scripts/release_notes.py --next-title v0.2.4      title of the next release
    python scripts/release_notes.py --migrations             "old-tag new-tag" pairs from "dawniej …" lines

Published releases are sections "## vX.Y.Z – Title" (a line below may say "dawniej android-N"
for releases published before SemVer). Any other "## ..." heading (normally "Następne wydanie") holds
changes that are not released yet, with optional "Tytuł: English title" and "Wersja: major|minor|patch"
lines. Points are grouped by "### <category>"; points under "Drobne zmiany" never start a release.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CATEGORIES = ("Dodano", "Zmieniono", "Usunięto", "Naprawiono", "Ulepszono", "Drobne zmiany")
MINOR = "Drobne zmiany"
VERSION = r"v(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.]+))?"
TAG_HEADING = re.compile(rf"^##\s+({VERSION})(?:\s+[–—-]\s+(.*))?$")
OLD_TAG = re.compile(r"dawniej\s+(android-\d+)")
TITLE_LINE = re.compile(r"^Tytuł:\s*(.+)$")
BUMP_LINE = re.compile(r"^Wersja:\s*(major|minor|patch)\s*$")
INSTALL = ("---\n**Instalacja na Androidzie:** otwórz tę stronę na telefonie, dotknij **AgenticOS.apk** i zezwól "
           "przeglądarce na instalację, gdy zapyta. Nowa wersja instaluje się na poprzedniej.")


def parse_version(tag: str) -> tuple[int, int, int] | None:
    m = re.fullmatch(VERSION, tag or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


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


def releases(text: str) -> list[dict[str, str]]:
    """Published releases in file order: tag, title and the pre-SemVer tag they replace."""
    found: list[dict[str, str]] = []
    for line in text.splitlines():
        m = TAG_HEADING.match(line)
        if m:
            found.append({"tag": m.group(1), "title": (m.group(6) or "").strip(), "old": ""})
        elif found and not found[-1]["old"] and (old := OLD_TAG.search(line)):
            found[-1]["old"] = old.group(1)
    return found


def unreleased_lines(text: str) -> list[str]:
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = not TAG_HEADING.match(line)
        elif inside:
            lines.append(line)
    return lines


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


def old_version_note(text: str, tag: str) -> str:
    """For releases published before SemVer: the APK still reports the build number it was built with."""
    old = next((r["old"] for r in releases(text) if r["tag"] == tag), "")
    if not old:
        return ""
    build = old.split("-", 1)[1]
    return (f"> **Uwaga:** to wydanie powstało przed wprowadzeniem numerów wersji vX.Y.Z i wcześniej nazywało się "
            f"„wydanie {build}”. Aplikacja z tego wydania pokazuje w ustawieniach Androida dawny numer wersji "
            f"**1.0.{build}**, bo jest on zapisany w samym pliku APK podczas budowania i nie da się go zmienić bez "
            f"zbudowania aplikacji od nowa. To ten sam plik co wcześniej, zmieniła się tylko nazwa wydania.")


def title_for_tag(text: str, tag: str) -> str:
    return next((r["title"] for r in releases(text) if r["tag"] == tag), "")


def new_points(text: str, previous_text: str) -> list[tuple[str, str]]:
    """Unreleased points that were not there when the previous release was published."""
    old = {p for _, _, p in parse(previous_text)}
    return [(c, p) for t, c, p in parse(text) if t is None and p not in old]


def notes_since(text: str, previous_text: str) -> str:
    return render(new_points(text, previous_text))


def worth_release(text: str, previous_text: str) -> bool:
    """A release is worth it when at least one new point is more than a minor change."""
    return any(c != MINOR for c, _ in new_points(text, previous_text))


def _line_value(pattern: re.Pattern[str], text: str) -> str:
    return next((m.group(1).strip() for line in unreleased_lines(text) if (m := pattern.match(line.strip()))), "")


def next_title(text: str, previous_text: str) -> str:
    """The English "Tytuł:" line when it was written for this release, else a generic English title."""
    title = _line_value(TITLE_LINE, text)
    if title and title != _line_value(TITLE_LINE, previous_text):
        return title
    categories = {c for c, _ in new_points(text, previous_text)}
    if "Dodano" in categories:
        return "New Features & Improvements"
    return "Fixes & Improvements" if categories - {MINOR} else "Minor Updates"


def next_version(text: str, previous_text: str, tags: list[str]) -> str:
    """Bump the newest known version: "Wersja:" line if new, else MINOR for "Dodano" points, else PATCH."""
    known = [v for v in (parse_version(t) for t in tags + [r["tag"] for r in releases(text)]) if v]
    major, minor, patch = max(known, default=(0, 0, 0))
    bump = _line_value(BUMP_LINE, text)
    if not bump or bump == _line_value(BUMP_LINE, previous_text):
        bump = "minor" if any(c == "Dodano" for c, _ in new_points(text, previous_text)) else "patch"
    if not known:
        return "v0.1.0"
    if bump == "major":
        return f"v{major + 1}.0.0"
    if bump == "minor":
        return f"v{major}.{minor + 1}.0"
    return f"v{major}.{minor}.{patch + 1}"


def file_at(ref: str, path: str = "CHANGELOG.md") -> str:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def git_tags() -> list[str]:
    result = subprocess.run(["git", "tag", "--list", "v*"], capture_output=True, text=True, check=False)
    return result.stdout.split()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="notes of a release with its own section in CHANGELOG.md")
    group.add_argument("--title", metavar="TAG", help="title of a release with its own section")
    group.add_argument("--since", metavar="PREVIOUS", help="notes of the next release (empty for the first)")
    group.add_argument("--worth-release", metavar="PREVIOUS", help="print yes/no: do the new points deserve a release")
    group.add_argument("--next-version", metavar="PREVIOUS", help="print the version of the next release")
    group.add_argument("--next-title", metavar="PREVIOUS", help="print the title of the next release")
    group.add_argument("--migrations", action="store_true", help="print 'old-tag new-tag' for releases to rename")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    args = parser.parse_args(argv)
    text = Path(args.changelog).read_text(encoding="utf-8")
    if args.migrations:
        sys.stdout.writelines(f"{r['old']} {r['tag']}\n" for r in releases(text) if r["old"])
        return 0
    if args.title:
        sys.stdout.write(title_for_tag(text, args.title) + "\n")
        return 0
    if args.tag:
        note = old_version_note(text, args.tag)
        sys.stdout.write(f"{notes_for_tag(text, args.tag)}\n\n{note + chr(10) + chr(10) if note else ''}{INSTALL}\n")
        return 0
    previous_ref = next(v for v in (args.since, args.worth_release, args.next_version, args.next_title) if v is not None)
    previous = file_at(previous_ref) if previous_ref else ""
    if args.worth_release is not None:
        sys.stdout.write("yes\n" if worth_release(text, previous) else "no\n")
    elif args.next_version is not None:
        sys.stdout.write(next_version(text, previous, git_tags()) + "\n")
    elif args.next_title is not None:
        sys.stdout.write(next_title(text, previous) + "\n")
    else:
        sys.stdout.write(f"{notes_since(text, previous)}\n\n{INSTALL}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
