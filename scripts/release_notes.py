"""Release versions, titles and notes for GitHub releases, taken from CHANGELOG.md.

Releases follow SemVer: tag ``vMAJOR.MINOR.PATCH`` (now ``v0.MINOR.PATCH``) and title
``vX.Y.Z – Short English Title``. See "Wersje i nazwy wydań" in CHANGELOG.md.

    python scripts/release_notes.py --tag v0.2.1             bilingual notes of a published release
    python scripts/release_notes.py --tag v0.2.1 --generated generated.md
    python scripts/release_notes.py --title v0.2.1           title of a published release
    python scripts/release_notes.py --since v0.2.4           points added to "Następne wydanie" since that release
    python scripts/release_notes.py --worth-release v0.2.4   "yes" if those points deserve their own release
    python scripts/release_notes.py --next-version v0.2.4    version of the next release, e.g. v0.2.5
    python scripts/release_notes.py --next-title v0.2.4      title of the next release
    python scripts/release_notes.py --migrations             "old-tag new-tag" pairs from "dawniej …" lines
    python scripts/release_notes.py --renumbers              "old-tag new-tag" pairs from "przenumerowane z …" lines
    python scripts/release_notes.py --apk-name v0.2.1        APK asset name, e.g. AgenticOS_v0.2.1.apk

Published releases are sections "## vX.Y.Z – Title" (a line below may say "dawniej android-N"
for releases published before SemVer, or "przenumerowane z vA.B.C" for a release that got a new number). Any other "## ..." heading (normally "Następne wydanie") holds
changes that are not released yet, with optional "Tytuł: English title" and "Wersja: major|minor|patch"
lines ("Wersja: beta", "Wersja: major rc" etc. publish a test build such as v0.3.0-beta.1 instead;
"Wersja: build" rebuilds the newest version as v0.2.6+build.1). A release section may carry a "> Uwaga: ..." line,
shown as a note on the release page, and a "> Instalacja: ..." line that replaces the closing install sentence
(e.g. when a new signing key means the old app must be uninstalled first). Points are grouped by "### <category>"; points under "Drobne zmiany" never start a release.
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
RENUMBERED = re.compile(rf"przenumerowane z\s+({VERSION})")
TITLE_LINE = re.compile(r"^Tytuł:\s*(.+)$")
PHASES = ("alpha", "beta", "rc")
BUMP_LINE = re.compile(r"^Wersja:\s*((?:major|minor|patch)?\s*(?:alpha|beta|rc)?|build)\s*$")
INSTALL = ("---\n**Instalacja na Androidzie:** otwórz tę stronę na telefonie, dotknij **{apk}** i zezwól "
           "przeglądarce na instalację, gdy zapyta. {how}")
INSTALL_OVER = "Nowa wersja instaluje się na poprzedniej."


def apk_name(tag: str) -> str:
    """File name of the release's APK asset, e.g. AgenticOS_v0.2.1.apk."""
    return f"AgenticOS_{tag.replace('+', '_')}.apk"  # "+" breaks downloads on some phones


def install(tag: str, text: str = "") -> str:
    """The install footer; a "> Instalacja:" line in the tag's section replaces the closing sentence."""
    how = next((r["install"] for r in releases(text) if r["tag"] == tag and r["install"]), INSTALL_OVER)
    return INSTALL.format(apk=apk_name(tag), how=how)


def parse_version(tag: str) -> tuple[int, int, int] | None:
    m = re.fullmatch(VERSION, tag or "")
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def parse(text: str) -> list[tuple[str | None, str, str]]:
    """Return (tag or None, category, point) for every bullet point.

    ``#### EN`` / ``#### PL`` blocks are the bilingual release-page text. They are not Polish
    changelog points, so bullets inside them are skipped here.
    """
    points, tag, category, in_section = [], None, "", False
    skipping = False
    for line in text.splitlines():
        if line.startswith("## "):
            m = TAG_HEADING.match(line)
            tag, category, in_section = (m.group(1) if m else None), "", True
            skipping = False
        elif line.startswith("#### "):
            skipping = True
        elif line.startswith("### "):
            skipping = False
            category = line[4:].strip()
        elif skipping:
            continue
        elif in_section and line.startswith("- ") and category:
            points.append((tag, category, line[2:].strip()))
        elif in_section and category and points and points[-1][0] == tag and re.match(r"^\s+- ", line):
            last = points[-1]  # an indented "  - " line is a sub-point of the point above
            points[-1] = (last[0], last[1], f"{last[2]}\n  - {line.strip()[2:].strip()}")
    return points


def releases(text: str) -> list[dict[str, str]]:
    """Published releases in file order: tag, title, the pre-SemVer tag they replace, the number they had before
    renumbering ("was"), "> Uwaga:" and "> Instalacja:"."""
    found: list[dict[str, str]] = []
    for line in text.splitlines():
        m = TAG_HEADING.match(line)
        if m:
            found.append({"tag": m.group(1), "title": (m.group(7) or "").strip(), "old": "", "was": "", "note": "",
                           "note_en": "", "install": "", "install_en": ""})
        elif found and line.startswith("> Uwaga:"):
            found[-1]["note"] = line[len("> Uwaga:"):].strip()
        elif found and line.startswith("> Note:"):
            found[-1]["note_en"] = line[len("> Note:"):].strip()
        elif found and line.startswith("> Instalacja:"):
            found[-1]["install"] = line[len("> Instalacja:"):].strip()
        elif found and line.startswith("> Install:"):
            found[-1]["install_en"] = line[len("> Install:"):].strip()
        elif found and not found[-1]["old"] and (old := OLD_TAG.search(line)):
            found[-1]["old"] = old.group(1)
        elif found and not found[-1]["was"] and (was := RENUMBERED.search(line)):
            found[-1]["was"] = was.group(1)
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


def renumbered_note(text: str, tag: str) -> str:
    """For releases that got a new number: the APK inside still reports the number it was built with."""
    was = next((r["was"] for r in releases(text) if r["tag"] == tag), "")
    if not was:
        return ""
    shown = was.lstrip("v")  # Android shows versionName without the "v" (APP_VERSION in android.yml)
    return (f"> **Uwaga:** to wydanie wcześniej nazywało się **{was}**. Numer zmienił się, gdy uporządkowaliśmy "
            f"numerację: drobne zmiany podnoszą teraz ostatnią cyfrę, a tylko większe nowe funkcje środkową. "
            f"To ten sam plik co wcześniej, zmieniła się tylko nazwa wydania.\n\n"
            f"> 📱 **Na telefonie** aplikacja może w ustawieniach Androida pokazywać stary numer (np. **{shown}**), "
            f"bo jest on zapisany w pliku APK.")


def release_note(text: str, tag: str) -> str:
    """The section's own "> Uwaga:" line, then the pre-SemVer or renumbering note, as quoted notes for the release page."""
    own = next((r["note"] for r in releases(text) if r["tag"] == tag), "")
    notes = [f"> **Uwaga:** {own}"] if own else []
    if old := old_version_note(text, tag):
        notes.append(old)
    if was := renumbered_note(text, tag):
        notes.append(was)
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
    """Bump the newest stable version: by the "Wersja:" line if it is new, else PATCH.

    PATCH covers fixes, improvements and small new things; MINOR (a bigger new feature) and MAJOR (a fundamental
    change or the first stable version) are chosen on purpose with "Wersja: minor" / "Wersja: major".

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
        bump = "patch"  # MINOR and MAJOR only on request: a "Wersja: minor" / "Wersja: major" line
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


REPO = "JavsonOf/agentic-os"
SECTION_ORDER = ("highlights", "features", "improvements", "fixes", "docs")
# "Zmieniono" on these releases is about the release process itself, so it is Docs & CI.
DOCS_CATEGORIES = {
    "v0.2.3": {"Zmieniono"},
    "v0.2.4": {"Zmieniono"},
    "v0.2.5": {"Zmieniono"},
    "v0.2.6": {"Zmieniono"},
}
CATEGORY_SECTION = {
    "Dodano": "features",
    "Ulepszono": "improvements",
    "Zmieniono": "improvements",
    "Usunięto": "improvements",
    "Naprawiono": "fixes",
    "Drobne zmiany": "docs",
}
BLOCK_NAMES = {
    ("EN", "Tytuł"): ("en", "title"),
    ("EN", "Highlights"): ("en", "highlights"),
    ("EN", "New Features"): ("en", "features"),
    ("EN", "Improvements"): ("en", "improvements"),
    ("EN", "Bug Fixes"): ("en", "fixes"),
    ("EN", "Docs & CI"): ("en", "docs"),
    ("PL", "Tytuł"): ("pl", "title"),
    ("PL", "Najważniejsze"): ("pl", "highlights"),
    ("PL", "Nowości"): ("pl", "features"),
    ("PL", "Ulepszenia"): ("pl", "improvements"),
    ("PL", "Poprawki"): ("pl", "fixes"),
    ("PL", "Dokumentacja i CI"): ("pl", "docs"),
}
HEADINGS = {
    "en": {
        "highlights": "## ✨ Highlights",
        "features": "## 🚀 New Features",
        "improvements": "## 🛠 Improvements",
        "fixes": "## 🐛 Bug Fixes",
        "docs": "## 📚 Docs & CI",
        "changes": "## What's Changed",
        "firsts": "## New Contributors",
    },
    "pl": {
        "highlights": "## ✨ Najważniejsze",
        "features": "## 🚀 Nowości",
        "improvements": "## 🛠 Ulepszenia",
        "fixes": "## 🐛 Poprawki",
        "docs": "## 📚 Dokumentacja i CI",
        "changes": "## Co się zmieniło",
        "firsts": "## Nowi autorzy",
    },
}
EMPTY = {
    "en": {
        "highlights": "- No highlights in this release.",
        "features": "- No new features in this release.",
        "improvements": "- No improvements in this release.",
        "fixes": "- No bug fixes in this release.",
        "docs": "- No docs or CI changes in this release.",
        "changes": "- No pull requests in this release.",
    },
    "pl": {
        "highlights": "- Brak najważniejszych zmian w tym wydaniu.",
        "features": "- Brak nowych funkcji w tym wydaniu.",
        "improvements": "- Brak ulepszeń w tym wydaniu.",
        "fixes": "- Brak poprawek w tym wydaniu.",
        "docs": "- Brak zmian w dokumentacji i CI w tym wydaniu.",
        "changes": "- Brak pull requestów w tym wydaniu.",
    },
}
INSTALL_EN_OVER = "The new version installs over the previous one."
INSTALL_PL_OVER = "Nowa wersja instaluje się nad poprzednią."


def _section_lines(text: str, tag: str | None) -> list[str]:
    """Lines inside one changelog section, without the ``##`` heading."""
    buf, capture = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if capture:
                break
            if tag is None:
                capture = line.strip() == "## Następne wydanie"
            else:
                match = TAG_HEADING.match(line)
                capture = bool(match and match.group(1) == tag)
            continue
        if capture:
            buf.append(line)
    return buf


def explicit_blocks(text: str, tag: str | None) -> dict[tuple[str, str], str]:
    """``#### EN`` / ``#### PL`` bodies written for one release. Missing keys are not explicit."""
    found: dict[tuple[str, str], str] = {}
    current: tuple[str, str] | None = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal buf, current
        if current is not None:
            found[current] = "\n".join(buf).strip()
        buf = []

    for line in _section_lines(text, tag):
        match = re.match(r"^#### (EN|PL) (.+)$", line)
        if match:
            flush()
            current = BLOCK_NAMES.get((match.group(1), match.group(2).strip()))
            continue
        if line.startswith("### "):
            flush()
            current = None
            continue
        if current is not None:
            buf.append(line)
    flush()
    return found


def _section_for(tag: str | None, category: str) -> str:
    if category in DOCS_CATEGORIES.get(tag or "", ()):
        return "docs"
    return CATEGORY_SECTION.get(category, "improvements")


def auto_sections(points: list[tuple[str, str]]) -> dict[str, str]:
    """Polish changelog points grouped into the five release sections."""
    groups: dict[str, list[str]] = {}
    for category, point in points:
        groups.setdefault(_section_for(None, category), []).append(point)
    return {key: "\n".join(f"- {point}" for point in items) for key, items in groups.items()}


def auto_sections_for_tag(text: str, tag: str | None) -> dict[str, str]:
    grouped: dict[str, list[str]] = {}
    for point_tag, category, point in parse(text):
        if point_tag != tag:
            continue
        grouped.setdefault(_section_for(tag, category), []).append(point)
    return {key: "\n".join(f"- {point}" for point in items) for key, items in grouped.items()}


def _release_row(text: str, tag: str | None) -> dict[str, str]:
    return next((row for row in releases(text) if row["tag"] == tag), {})


def note_bullets(text: str, tag: str | None, lang: str) -> str:
    """Version-number notes (pre-SemVer, renumber, ``> Uwaga``) as section bullets."""
    row = _release_row(text, tag)
    if not row:
        return ""
    lines: list[str] = []
    if lang == "pl":
        if row.get("note"):
            lines.append(f"- {row['note']}")
        if row.get("old"):
            build = row["old"].split("-", 1)[1]
            lines.append(
                f"- To wydanie powstało przed wprowadzeniem numerów wersji vX.Y.Z i wcześniej nazywało się "
                f"„wydanie {build}”. Aplikacja z tego wydania pokazuje w ustawieniach Androida dawny numer wersji "
                f"**1.0.{build}**, bo jest on zapisany w pliku APK podczas budowania i nie da się go zmienić bez "
                f"zbudowania aplikacji od nowa. To ten sam plik co wcześniej, zmieniła się tylko nazwa wydania."
            )
        if row.get("was"):
            shown = row["was"].lstrip("v")
            lines.append(
                f"- To wydanie wcześniej nazywało się **{row['was']}**. Numer zmienił się, gdy uporządkowaliśmy "
                f"numerację: drobne zmiany podnoszą teraz ostatnią cyfrę, a tylko większe nowe funkcje środkową. "
                f"To ten sam plik co wcześniej, zmieniła się tylko nazwa wydania."
            )
            lines.append(
                f"- Na telefonie aplikacja może w ustawieniach Androida pokazywać stary numer (np. **{shown}**), "
                f"bo jest on zapisany w pliku APK."
            )
    else:
        if row.get("note_en"):
            lines.append(f"- {row['note_en']}")
        if row.get("old"):
            build = row["old"].split("-", 1)[1]
            lines.append(
                f"- This release was published before vX.Y.Z version numbers and used to be called "
                f"“release {build}”. The app from this release shows the old version **1.0.{build}** in Android "
                f"settings, because that number was written into the APK when it was built and cannot be changed "
                f"without building the app again. It is the same file as before; only the release name changed."
            )
        if row.get("was"):
            shown = row["was"].lstrip("v")
            lines.append(
                f"- This release used to be called **{row['was']}**. The number changed when numbering was tidied "
                f"up: small changes now bump the last digit, and only larger new features bump the middle one. "
                f"It is the same file as before; only the release name changed."
            )
            lines.append(
                f"- On the phone, Android settings may still show the old number (for example **{shown}**), "
                f"because that number is stored in the APK file."
            )
    return "\n".join(lines)


def _with_notes(body: str, notes: str, empty: str) -> str:
    if not notes:
        return body
    if body == empty:
        return notes
    return f"{body}\n{notes}"


def pull_request_lines(generated: str) -> tuple[list[str], list[str]]:
    """PR bullets and first-contribution bullets from a generate-notes body, PRs oldest-number first."""
    prs, firsts = [], []
    for line in (generated or "").splitlines():
        if not line.startswith("* ") or "/pull/" not in line:
            continue
        if "made their first contribution" in line:
            firsts.append(line)
        else:
            prs.append(line)
    prs.sort(key=lambda line: int(re.search(r"/pull/(\d+)", line).group(1)))
    return prs, firsts


def previous_release_tag(text: str, tag: str) -> str:
    tags = [row["tag"] for row in releases(text)]
    if tag not in tags:
        return ""
    index = tags.index(tag)
    return tags[index + 1] if index + 1 < len(tags) else ""


def full_changelog_url(tag: str, previous: str, generated: str) -> str:
    match = re.search(r"^\*\*Full Changelog\*\*:\s*(\S+)", generated or "", re.MULTILINE)
    if match:
        return match.group(1)
    if previous:
        return f"https://github.com/{REPO}/compare/{previous}...{tag}"
    return f"https://github.com/{REPO}/commits/{tag}"


def _fill_sections(lang: str, blocks: dict[tuple[str, str], str], auto: dict[str, str], notes: str) -> dict[str, str]:
    filled: dict[str, str] = {}
    for key in SECTION_ORDER:
        explicit = (lang, key) in blocks
        if explicit:
            filled[key] = blocks[(lang, key)] or EMPTY[lang][key]
        elif lang == "pl" and auto.get(key):
            filled[key] = auto[key]
        else:
            filled[key] = EMPTY[lang][key]
        if key == "docs":
            filled[key] = _with_notes(filled[key], notes, EMPTY[lang][key])
    if (lang, "highlights") not in blocks:
        for key in ("features", "fixes", "improvements", "docs"):
            if lang == "pl" and auto.get(key):
                filled["highlights"] = auto[key].split("\n", 1)[0][2:].strip()
                break
    return filled


def _render_language(lang: str, label: str, tag: str, title: str, sections: dict[str, str], changes: str,
                     firsts: list[str], how: str, link: str) -> str:
    apk = apk_name(tag)
    if lang == "en":
        install = (f"**Install on Android:** open this page on your phone, tap **{apk}** and allow the browser "
                   f"to install it. {how}")
        history = f"**Full Changelog**: {link}"
    else:
        install = (f"**Instalacja na Androidzie:** otwórz tę stronę na telefonie, stuknij **{apk}** i zezwól "
                   f"przeglądarce na instalację. {how}")
        history = f"**Pełna historia zmian**: {link}"
    parts = [label, "", f"# {tag} – {title}", ""]
    for key in SECTION_ORDER:
        parts.extend((HEADINGS[lang][key], sections[key], ""))
    parts.extend((HEADINGS[lang]["changes"], changes, ""))
    if firsts:
        parts.extend((HEADINGS[lang]["firsts"], "\n".join(firsts), ""))
    parts.extend(("---", install, "", history))
    return "\n".join(parts)


def bilingual_body(text: str, tag: str | None, generated: str = "", *, auto_points: list[tuple[str, str]] | None = None,
                   version: str = "", title: str = "") -> str:
    """GitHub release body: English block, then Polish, with every section filled in.

    ``tag`` is a published heading. For the upcoming release pass ``tag=None`` and the points that are new
    since the previous release (``auto_points``), plus ``version`` and ``title``. ``generated`` is the body from
    GitHub's generate-notes API; its pull requests become "What's Changed" in both languages.
    """
    version = version or tag or ""
    blocks = explicit_blocks(text, tag)
    auto = auto_sections(auto_points) if auto_points is not None else auto_sections_for_tag(text, tag)
    # auto_sections() ignores the tag override for docs categories; re-group when a tag is known.
    if auto_points is not None and tag:
        grouped: dict[str, list[str]] = {}
        for category, point in auto_points:
            grouped.setdefault(_section_for(tag, category), []).append(point)
        auto = {key: "\n".join(f"- {point}" for point in items) for key, items in grouped.items()}
    row = _release_row(text, tag)
    en_title = blocks.get(("en", "title")) or title or (row.get("title") if row else "") or version
    pl_title = blocks.get(("pl", "title")) or en_title
    en_sections = _fill_sections("en", blocks, auto, note_bullets(text, tag, "en"))
    pl_sections = _fill_sections("pl", blocks, auto, note_bullets(text, tag, "pl"))
    if ("en", "highlights") not in blocks and en_sections["highlights"] == EMPTY["en"]["highlights"] and en_title:
        en_sections["highlights"] = en_title
    prs, firsts = pull_request_lines(generated)
    changes = {
        "en": "\n".join(prs) if prs else EMPTY["en"]["changes"],
        "pl": "\n".join(prs) if prs else EMPTY["pl"]["changes"],
    }
    link = full_changelog_url(version, previous_release_tag(text, version) if version else "", generated)
    how_en = (row.get("install_en") if row else "") or INSTALL_EN_OVER
    how_pl = (row.get("install") if row else "") or INSTALL_PL_OVER
    english = _render_language("en", "ENG", version, en_title, en_sections, changes["en"], firsts, how_en, link)
    polish = _render_language("pl", "PL", version, pl_title, pl_sections, changes["pl"], firsts, how_pl, link)
    return f"{english}\n\n{polish}\n"


def file_at(ref: str, path: str = "CHANGELOG.md") -> str:
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, check=False)
    return result.stdout if result.returncode == 0 else ""


def git_tags() -> list[str]:
    result = subprocess.run(["git", "tag", "--list", "v*"], capture_output=True, text=True, check=False)
    return result.stdout.split()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="bilingual notes of a release with its own section in CHANGELOG.md")
    parser.add_argument("--generated", help="generate-notes body; its pull requests fill What's Changed")
    group.add_argument("--title", metavar="TAG", help="title of a release with its own section")
    group.add_argument("--since", metavar="PREVIOUS", help="notes of the next release (empty for the first)")
    group.add_argument("--worth-release", metavar="PREVIOUS", help="print yes/no: do the new points deserve a release")
    group.add_argument("--next-version", metavar="PREVIOUS", help="print the version of the next release")
    group.add_argument("--next-title", metavar="PREVIOUS", help="print the title of the next release")
    group.add_argument("--migrations", action="store_true", help="print 'old-tag new-tag' for releases to rename")
    group.add_argument("--renumbers", action="store_true", help="print 'old-tag new-tag' for renumbered releases, oldest first")
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
    if args.renumbers:
        sys.stdout.writelines(f"{r['was']} {r['tag']}\n" for r in reversed(releases(text)) if r["was"])
        return 0
    if args.title:
        sys.stdout.write(title_for_tag(text, args.title) + "\n")
        return 0
    generated = Path(args.generated).read_text(encoding="utf-8") if args.generated else ""
    if args.tag:
        sys.stdout.write(bilingual_body(text, args.tag, generated))
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
        sys.stdout.write(bilingual_body(
            text, None, generated, auto_points=new_points(text, previous), version=version,
            title=next_title(text, previous)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
