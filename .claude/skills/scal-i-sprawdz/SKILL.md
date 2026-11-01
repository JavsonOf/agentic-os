---
name: scal-i-sprawdz
description: Scala pull request, gdy wszystkie checki CI są zielone, a potem sprawdza, czy opisy wydań (release notes / changelog) się zaktualizowały i czy pojawiło się najnowsze wydanie (release) na GitHubie — po kolei, z przerwą 30–60 s między krokami. Uruchamiaj ZAWSZE, gdy użytkownik wpisze "/scal-i-sprawdz", a także gdy pisze np. "scal jak będzie zielone", "zmerguj i sprawdź release", "merge when green and check the release", "czy wydanie się pojawiło po merge'u".
---

# /scal-i-sprawdz

Sekwencja trzech kroków wykonywanych **ściśle po kolei**. Nie przechodź do następnego kroku, dopóki poprzedni się nie zakończył, i zawsze odczekaj 30–60 sekund między krokami (domyślnie `sleep 45`), bo GitHub Actions / release-please potrzebują chwili na reakcję.

## Ustal kontekst (przed krokiem 1)

- **Repozytorium i PR**: jeśli użytkownik podał numer/link PR — użyj go. Jeśli nie, weź PR powiązany z bieżącą gałęzią (`gh pr view --json number,url,headRefName`). Jeśli jest kilka kandydatów albo żadnego — zapytaj jednym krótkim pytaniem.
- **Narzędzia**: preferuj `gh` CLI. Gdy go nie ma, użyj dostępnego konektora GitHub/MCP. Gdy nie ma żadnego dostępu do GitHuba, powiedz to wprost i podaj użytkownikowi komendy do wykonania ręcznie — nie udawaj, że coś zostało scalone.
- Zanotuj **najnowsze wydanie przed merge'em** (`gh release list --limit 1`), żeby w kroku 3 mieć z czym porównać.

## Krok 1 — Scal, gdy będzie zielone

1. Sprawdź stan checków: `gh pr checks <PR>`.
2. Jeśli checki jeszcze trwają — czekaj (`gh pr checks <PR> --watch` albo odpytuj co ~30 s). Limit czekania: ok. 15 minut; potem zapytaj użytkownika, czy czekać dalej.
3. Jeśli któryś check jest **czerwony** — **NIE scalaj**. Przerwij całą sekwencję, pokaż, który check padł (nazwa + link do logów), i zakończ.
4. Gdy wszystko zielone i PR jest mergeable: `gh pr merge <PR> --merge` (albo metodą używaną w repo — jeśli repo wymusza squash/rebase, użyj jej; w razie wątpliwości sprawdź `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`). Gdy repo ma włączony auto-merge, można zamiast tego `gh pr merge <PR> --auto`.
5. Potwierdź merge: `gh pr view <PR> --json state,mergedAt` → `state` = `MERGED`.

⏳ Odczekaj 30–60 s (`sleep 45`).

## Krok 2 — Sprawdź, czy opisy wydań się zaktualizowały

Sprawdź to, co w danym repo pełni rolę opisu wydań:
- **release-please**: PR wydania (`gh pr list --search "release-please" --state open` lub z etykietą `autorelease: pending`) — czy jego opis/CHANGELOG zawiera zmiany ze scalonego PR (tytuł, numer PR, commit).
- **CHANGELOG.md** w gałęzi domyślnej — czy jest nowy wpis.
- **Draft release** (np. release-drafter): `gh release list` → najnowszy draft i jego treść (`gh release view <tag>`).

Wynik: ✅ zaktualizowane (pokaż krótko, jaki wpis doszedł) / ⚠️ jeszcze nie. Jeśli „jeszcze nie”, sprawdź workflow (`gh run list --limit 5`) — czy się wykonuje, czy padł — i zgłoś to. Można raz ponowić sprawdzenie po kolejnych 30–60 s.

⏳ Odczekaj 30–60 s (`sleep 45`).

## Krok 3 — Sprawdź, czy pojawiło się najnowsze wydanie

1. `gh release list --limit 3` i porównaj z wydaniem zanotowanym przed merge'em.
2. Jeśli jest nowe: podaj tag, nazwę, datę i link (`gh release view <tag> --json tagName,name,publishedAt,url`).
3. Jeśli nie ma — to często **normalne** (np. release-please tworzy wydanie dopiero po scaleniu PR wydania). Powiedz to jasno i wskaż, co blokuje (otwarty PR wydania, trwający lub nieudany workflow).

## Raport końcowy

Krótko, po polsku, w formie:

```
1. Merge: ✅ PR #123 scalony (14:02)
2. Opisy wydań: ✅ / ⚠️ <co znaleziono>
3. Nowe wydanie: ✅ v1.4.0 <link> / ⚠️ brak — <dlaczego>
```

## Zasady

- Nigdy nie scalaj PR z czerwonymi lub nieukończonymi checkami.
- Nie twórz wydań ani tagów ręcznie, nie edytuj changelogu — ten skill tylko scala i sprawdza.
- Nie pomijaj przerw między krokami.
