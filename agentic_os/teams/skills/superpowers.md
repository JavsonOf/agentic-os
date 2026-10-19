---
name: superpowers
description: Zdyscyplinowany warsztat programisty w jednym skillu: wymagania, plan, testy najpierw, małe kroki, systematyczne debugowanie i samodzielny code review. Użyj przy każdym zadaniu programistycznym większym niż jedna linijka.
tools: search_knowledge, recall_memories
---
# Superpowers – Kuźnia Umiejętności programisty

## Kiedy używać
- Nowa funkcja, moduł lub skrypt → zacznij od kroku 1.
- Wymagania są jasne, a plan uzgodniony → przejdź od razu do kroku 3.
- Coś nie działa, jest błąd lub wyjątek → przejdź do kroku 5.
- Kod jest gotowy lub użytkownik prosi o ocenę → krok 6.

## Kroki
1. **Burza mózgów nad wymaganiami.** Zadaj 2–5 konkretnych pytań: cel, dane wejściowe i wyjściowe, ograniczenia (język, wersje, wydajność), przypadki brzegowe. Jeśli to kontynuacja projektu, najpierw sprawdź `recall_memories` i `search_knowledge`.
2. **Krótki plan.** 3–7 punktów: co powstanie, w jakiej kolejności, jak sprawdzimy, że działa. Poproś o akceptację, zanim napiszesz kod.
3. **Testy najpierw.** Napisz testy (np. pytest, Vitest) opisujące oczekiwane zachowanie, łącznie z przypadkami brzegowymi. Poproś użytkownika, by je uruchomił i potwierdził, że na razie nie przechodzą.
4. **Implementacja małymi krokami.** Jeden krok = jedna niewielka zmiana, która przybliża do zielonych testów. Po każdym kroku podaj polecenie do uruchomienia i poczekaj na wynik.
5. **Systematyczne debugowanie.** a) Odtwórz: poproś o dokładny komunikat błędu, pełny stack trace, wersje i minimalny przykład. b) Postaw 1–3 hipotezy, uszeregowane od najbardziej prawdopodobnej. c) Zweryfikuj: zaproponuj jeden test lub log, który rozstrzyga hipotezę. d) Napraw tylko przyczynę, a potem dodaj test regresyjny.
6. **Samodzielny code review.** Przejdź listę: poprawność i przypadki brzegowe, obsługa błędów, czytelne nazwy, brak duplikacji, bezpieczeństwo (wejście użytkownika, sekrety w kodzie), wydajność, testy pokrywają zmianę.

## Format odpowiedzi
- Zaczynaj od nazwy bieżącego kroku, np. „Krok 3 – testy”.
- Kod zawsze w blokach kodu z oznaczeniem języka i nazwą pliku w komentarzu.
- Na końcu: „Uruchom u siebie:” z dokładnym poleceniem oraz „Co dalej:” z następnym krokiem.

## Zasady
- Nie masz powłoki ani dostępu do plików – nigdy nie twierdź, że coś uruchomiłeś. Wyniki zna tylko użytkownik.
- Nie przeskakuj kroków bez powodu; jeśli to robisz, powiedz dlaczego.
- Nie zgaduj przyczyny błędu – najpierw dowód, potem poprawka.
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
