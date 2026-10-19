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
    python scripts/release_notes.py --apk-name v0.2.1        APK asset name, e.g. AgenticOS_v0.2.1.apk

Published releases are sections "## vX.Y.Z – Title" (a line below may say "dawniej android-N"
for releases published before SemVer). Any other "## ..." heading (normally "Następne wydanie") holds
changes that are not released yet, with optional "Tytuł: English title" and "Wersja: major|minor|patch"
lines ("Wersja: beta", "Wersja: major rc" etc. publish a test build such as v0.3.0-beta.1 instead;
"Wersja: build" rebuilds the newest version as v0.2.6+build.1). A release section may carry a "> Uwaga: ..." line,
shown as a note on the release page. Points are grouped by "### <category>"; points under "Drobne zmiany" never start a release.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CATEGORIES = ("Dodano", "Zmieniono", "Usunięto", "Naprawiono", "Ulepszono", "Drobne zmiany")
MINOR = "Drobne zmiany"
VERSION = r"v(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.]+))?(?:\+([0-9A-Za-z.]+))?"
TAG_HEADING = re.compile(rf"^##\s+({VERSION})(?:\s+[–—-]\s+(.*))?$")
OLD_TAG = re.compile(r"dawniej\s+(android-\d+)")
TITLE_LINE = re.compile(r"^Tytuł:\s*(.+)$")
PHASES = ("alpha", "beta", "rc")
BUMP_LINE = re.compile(r"^Wersja:\s*((?:major|minor|patch)?\s*(?:alpha|beta|rc)?|build)\s*$")
INSTALL = ("---\n**Instalacja na Androidzie:** otwórz tę stronę na telefonie, dotknij **{apk}** i zezwól "
           "przeglądarce na instalację, gdy zapyta. Nowa wersja instaluje się na poprzedniej.")


def apk_name(tag: str) -> str:
    """File name of the release's APK asset, e.g. AgenticOS_v0.2.1.apk."""
    return f"AgenticOS_{tag.replace('+', '_')}.apk"  # "+" breaks downloads on some phones


def install(tag: str) -> str:
    return INSTALL.format(apk=apk_name(tag))


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
        elif in_section and category and points and points[-1][0] == tag and re.match(r"^\s+- ", line):
            last = points[-1]  # an indented "  - " line is a sub-point of the point above
            points[-1] = (last[0], last[1], f"{last[2]}\n  - {line.strip()[2:].strip()}")
    return points


def releases(text: str) -> list[dict[str, str]]:
    """Published releases in file order: tag, title, the pre-SemVer tag they replace and a "> Uwaga:" note."""
    found: list[dict[str, str]] = []
    for line in text.splitlines():
        m = TAG_HEADING.match(line)
        if m:
            found.append({"tag": m.group(1), "title": (m.group(7) or "").strip(), "old": "", "note": ""})
        elif found and line.startswith("> Uwaga:"):
            found[-1]["note"] = line[len("> Uwaga:"):].strip()
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


def release_note(text: str, tag: str) -> str:
    """The section's own "> Uwaga:" line, then the pre-SemVer note, as quoted notes for the release page."""
    own = next((r["note"] for r in releases(text) if r["tag"] == tag), "")
    notes = [f"> **Uwaga:** {own}"] if own else []
    if old := old_version_note(text, tag):
        notes.append(old)
    return "\n\n".join(notes)


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
    """Bump the newest stable version: "Wersja:" line if new, else MINOR for "Dodano" points, else PATCH.

    "Wersja: alpha|beta|rc" (optionally after the bump, e.g. "Wersja: major rc") makes a test build of the
    next version: v0.3.0-beta.1, then -beta.2, ... Without it, the stable release keeps the tested number.
    "Wersja: build" rebuilds the newest stable version without changing it: v0.2.6+build.1, +build.2, ...
    """
    all_tags = tags + [r["tag"] for r in releases(text)]
    stable = [v for v in (parse_version(t) for t in all_tags if "-" not in t) if v]
    major, minor, patch = max(stable, default=(0, 0, 0))
    line = _line_value(BUMP_LINE, text)
    words = line.split() if line != _line_value(BUMP_LINE, previous_text) else []
    if "build" in words and stable:
        base = f"v{major}.{minor}.{patch}"
        builds = [int(m.group(1)) for t in all_tags if (m := re.fullmatch(rf"{re.escape(base)}\+build\.(\d+)", t))]
        return f"{base}+build.{max(builds, default=0) + 1}"
    phase = next((w for w in words if w in PHASES), "")
    bump = next((w for w in words if w not in PHASES), "")
    if not bump:
        bump = "minor" if any(c == "Dodano" for c, _ in new_points(text, previous_text)) else "patch"
    if not stable:
        version = "v0.1.0"
    elif bump == "major":
        version = f"v{major + 1}.0.0"
    elif bump == "minor":
        version = f"v{major}.{minor + 1}.0"
    else:
        version = f"v{major}.{minor}.{patch + 1}"
    # test builds already fixed the next number: further builds and the stable release keep it
    tested = [v for v in (parse_version(t) for t in all_tags if "-" in t) if v and v > (major, minor, patch)]
    if tested:
        version = "v{}.{}.{}".format(*max(tested))
    if not phase:
        return version
    builds = [int(m.group(1)) for t in all_tags if (m := re.fullmatch(rf"{re.escape(version)}-{phase}\.(\d+)", t))]
    return f"{version}-{phase}.{max(builds, default=0) + 1}"


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
    group.add_argument("--apk-name", metavar="TAG", help="print the APK asset name of a release")
    parser.add_argument("--changelog", default="CHANGELOG.md")
    args = parser.parse_args(argv)
    if args.apk_name:
        sys.stdout.write(apk_name(args.apk_name) + "\n")
        return 0
    text = Path(args.changelog).read_text(encoding="utf-8")
    if args.migrations:
        sys.stdout.writelines(f"{r['old']} {r['tag']}\n" for r in releases(text) if r["old"])
        return 0
    if args.title:
        sys.stdout.write(title_for_tag(text, args.title) + "\n")
        return 0
    if args.tag:
        note = release_note(text, args.tag)
        sys.stdout.write(f"{notes_for_tag(text, args.tag)}\n\n{note + chr(10) + chr(10) if note else ''}{install(args.tag)}\n")
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
        version = next_version(text, previous, git_tags())
        sys.stdout.write(f"{notes_since(text, previous)}\n\n{install(version)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
