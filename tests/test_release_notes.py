import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_notes", ROOT / "scripts" / "release_notes.py")
release_notes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_notes)

OLD = """## Następne wydanie

### Dodano
- Stara rzecz.

## android-1 · 1.10.2026

### Naprawiono
- Błąd z pierwszego wydania.
"""
NEW = """## Następne wydanie

### Naprawiono
- Nowa poprawka.

### Dodano
- Stara rzecz.
- Nowa rzecz.

## android-2 · 2.10.2026

### Ulepszono
- Coś z drugiego wydania.

## android-1 · 1.10.2026

### Naprawiono
- Błąd z pierwszego wydania.
"""


def test_notes_since_lists_only_new_unreleased_points_grouped_by_category():
    notes = release_notes.notes_since(NEW, OLD)
    assert notes == "### Dodano\n- Nowa rzecz.\n\n### Naprawiono\n- Nowa poprawka."
    assert release_notes.notes_since(OLD, OLD) == "Drobne poprawki i aktualizacje."
    assert "Coś z drugiego wydania" not in release_notes.notes_since(NEW, "")  # released points are never repeated


def test_notes_for_tag_and_the_real_changelog():
    assert release_notes.notes_for_tag(NEW, "android-1") == "### Naprawiono\n- Błąd z pierwszego wydania."
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for tag in ("android-2", "android-8", "android-9"):
        notes = release_notes.notes_for_tag(text, tag)
        assert notes.startswith("### ") and "Drobne poprawki" not in notes
    for _, category, _ in release_notes.parse(text):
        assert category in release_notes.CATEGORIES


def test_minor_changes_wait_for_the_next_real_release():
    base = "## Następne wydanie\n\n### Naprawiono\n- Stara poprawka.\n"
    minor = base + "\n### Drobne zmiany\n- Literówka w opisie.\n"
    assert release_notes.worth_release(minor, base) is False
    real = minor + "\n### Dodano\n- Nowa funkcja.\n"
    assert release_notes.worth_release(real, base) is True
    notes = release_notes.notes_since(real, base)
    assert notes.index("### Dodano") < notes.index("### Drobne zmiany") and "Literówka" in notes
    assert release_notes.worth_release(base, base) is False
