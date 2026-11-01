# PROGRESS – plik roboczy (usunąć osobnym commitem przed scaleniem)

Ostatnia aktualizacja: 2026-11-01 ~01:00 UTC, branch `claude/ux-edit-undo`.

## Cel
Pomysły UX 3 i 4 z przeglądu PR #32/#33 (autozapis skilli z „Cofnij”, opis skilla po przytrzymaniu),
edycja wysłanej wiadomości w czacie oraz to, co uznam za przydatne z listy priorytetów.

## Stos PR-ów (kolejność scalania)
| PR | Branch | Head | Baza | Stan |
|----|--------|------|------|------|
| #32 | claude/audit-medium-low | 4d91415 | main (e22a739) | draft, CI zielone, czeka na „scal” → v0.4.2 |
| #33 | claude/agent-screen | 1f68246 | claude/audit-medium-low | draft, CI zielone, czeka na „scal” |
| #34 | claude/ux-edit-undo | ff7f320 (+ ten plik) | claude/agent-screen | draft, CI zielone, czeka na „scal” |

#33 i #34 mają wspólną sekcję „Następne wydanie” w CHANGELOG → razem v0.5.0.

## Zrobione (#34)
- [x] `ConversationBuffer.rewind()`, `AgenticOS.rewind_chat()`, `POST /chat/rewind`
- [x] Edycja wiadomości w czacie (ołówek, edytor w miejscu, Anuluj/Esc, blokada podczas odpowiedzi)
- [x] Skille: autozapis + snackbar „Cofnij” (5 s), usunięty przycisk „Zapisz agenta”
- [x] Opis skilla po przytrzymaniu / prawym kliku (arkusz z opisem, narzędziami, instrukcjami)
- [x] Podgląd „Następne uruchomienie” w formularzu harmonogramu
- [x] Podpowiedź „wpisz klucz ponownie” przy zmianie adresu API dostawcy
- [x] Poprawka: `saveChat([])` nic nie zapisywał
- [x] sw.js v19, CHANGELOG, test `test_editing_a_message_forgets_the_later_exchanges`
- [x] pytest 159/159, ruff, node --check, Playwright (jasny/ciemny), CI zielone

## Zostało
- [ ] Czekać na „scal” od użytkownika (nie scalać samodzielnie)
- [ ] Przed scaleniem #34: usunąć PROGRESS.md osobnym commitem
- [ ] Scalanie po kolei: #32 → #33 → #34, potem sprawdzić wydania i opisy
- Otwarte poza tym: kopia zapasowa keystore (czeka na `ls ~/agentic-os-signing/` od użytkownika),
  domyślne uprawnienie agenta `ask` vs `auto`, poprawki Androida (kamera/mikrofon/gest wstecz), PR #22 wstrzymany.

## Następny krok
Czekam na potwierdzenie użytkownika.
