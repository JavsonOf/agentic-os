import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_notes", ROOT / "scripts" / "release_notes.py")
release_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes)

OLD = """## Następne wydanie

Tytuł: Czat: Stary tytuł

### Dodano
- Stara rzecz.

## v0.1.0 — Start: Pierwsze wydanie
_1.10.2026 · dawniej android-1_

### Naprawiono
- Błąd z pierwszego wydania.
"""
NEW = """## Następne wydanie

Tytuł: Modele: Nowy wybór modelu

### Naprawiono
- Nowa poprawka.

### Dodano
- Stara rzecz.
- Nowa rzecz.

## v0.1.1 — Android: Coś z drugiego wydania
_2.10.2026 · dawniej android-2_

### Ulepszono
- Coś z drugiego wydania.

## v0.1.0 — Start: Pierwsze wydanie
_1.10.2026 · dawniej android-1_

### Naprawiono
- Błąd z pierwszego wydania.
"""


def test_notes_since_lists_only_new_unreleased_points_grouped_by_category():
    notes = release_notes.notes_since(NEW, OLD)
    assert notes == "### Dodano\n- Nowa rzecz.\n\n### Naprawiono\n- Nowa poprawka."
    assert release_notes.notes_since(OLD, OLD) == "Drobne poprawki i aktualizacje."
    assert "Coś z drugiego wydania" not in release_notes.notes_since(NEW, "")  # released points are never repeated


def test_published_releases_titles_notes_and_migrations():
    assert release_notes.notes_for_tag(NEW, "v0.1.0") == "### Naprawiono\n- Błąd z pierwszego wydania."
    assert release_notes.title_for_tag(NEW, "v0.1.1") == "Android: Coś z drugiego wydania"
    assert [(r["old"], r["tag"]) for r in release_notes.releases(NEW)] == [("android-2", "v0.1.1"), ("android-1", "v0.1.0")]


def test_next_version_follows_semver_and_continues_the_numbering():
    # "Dodano" means a new feature: MINOR; no git tags yet, so the CHANGELOG headings are the history
    assert release_notes.next_version(NEW, OLD, []) == "v0.2.0"
    fixes_only = NEW.replace("- Nowa rzecz.\n", "")
    assert release_notes.next_version(fixes_only, OLD, []) == "v0.1.2"
    assert release_notes.next_version(fixes_only, OLD, ["v0.1.5", "android-9"]) == "v0.1.6"
    forced = NEW.replace("Tytuł: Modele", "Wersja: major\nTytuł: Modele")
    assert release_notes.next_version(forced, OLD, []) == "v1.0.0"
    assert release_notes.next_version("## Następne wydanie\n", "", []) == "v0.1.0"


def test_next_title_uses_a_fresh_title_line_or_the_first_point():
    assert release_notes.next_title(NEW, OLD) == "Modele: Nowy wybór modelu"
    stale = NEW.replace("Tytuł: Modele: Nowy wybór modelu", "Tytuł: Czat: Stary tytuł")
    assert release_notes.next_title(stale, OLD) == "Zmiany: Nowa poprawka"
    assert release_notes.next_title(OLD, OLD) == "Poprawki: Drobne poprawki i aktualizacje"


def test_minor_changes_wait_for_the_next_real_release():
    base = "## Następne wydanie\n\n### Naprawiono\n- Stara poprawka.\n"
    minor = base + "\n### Drobne zmiany\n- Literówka w opisie.\n"
    assert release_notes.worth_release(minor, base) is False
    real = minor + "\n### Dodano\n- Nowa funkcja.\n"
    assert release_notes.worth_release(real, base) is True
    notes = release_notes.notes_since(real, base)
    assert notes.index("### Dodano") < notes.index("### Drobne zmiany") and "Literówka" in notes
    assert release_notes.worth_release(base, base) is False


def test_the_real_changelog_is_consistent():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    published = release_notes.releases(text)
    tags = [r["tag"] for r in published]
    assert tags[-1] == "v0.1.0" and len(set(tags)) == len(tags)
    versions = [release_notes.parse_version(t) for t in tags]
    assert versions == sorted(versions, reverse=True)  # newest first, no duplicates
    for r in published:
        assert ": " in r["title"] and "Agentic OS –" not in r["title"]  # "Obszar: opis"
        assert release_notes.notes_for_tag(text, r["tag"]).startswith("### ")
    for _, category, _ in release_notes.parse(text):
        assert category in release_notes.CATEGORIES
