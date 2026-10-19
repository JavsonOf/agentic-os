---
name: cash-flow-snapshot
description: Tworzy migawkę przepływów pieniężnych firmy (saldo, burn, runway, największe koszty, ostrzeżenia) z danych o przychodach i wydatkach w CSV lub w formie listy; użyj, gdy chcesz szybko sprawdzić kondycję finansową.
tools: csv_summary, calculator, recall_memories, remember_fact
---
# Migawka przepływów pieniężnych

## Kiedy używać
- Użytkownik wkleja wyciąg, CSV albo listę wpływów i wydatków i pyta „jak stoję z kasą?”.
- Przed decyzją o dużym wydatku, zatrudnieniu lub kredycie.
- Przy comiesięcznym przeglądzie finansów firmy.

## Kroki
1. Sprawdź `recall_memories`, czy znasz już saldo początkowe, walutę lub kategorie kosztów tej firmy.
2. Jeśli dane są w CSV, użyj `csv_summary`, aby poznać kolumny (data, kwota, kategoria, opis) i zakres dat.
3. Ustal brakujące informacje i zapytaj o nie: saldo na dziś, okres analizy, czy kwoty są netto czy brutto, które pozycje są jednorazowe.
4. Policz za pomocą `calculator` (nie w pamięci): sumę wpływów, sumę wydatków i wynik netto dla każdego miesiąca.
5. Policz średni miesięczny burn: średnia wydatków minus średnia wpływów (tylko gdy wynik jest ujemny).
6. Policz runway: saldo na dziś podzielone przez średni burn netto (w miesiącach). Jeśli przepływ jest dodatni, napisz, że runway nie ma ograniczenia przy obecnym tempie.
7. Wypisz 5 największych kategorii kosztów i ich udział procentowy w wydatkach.
8. Zaproponuj zapisanie kluczowych wartości (saldo, burn, data) przez `remember_fact` do kolejnych porównań.

## Format odpowiedzi
- **Podsumowanie** w 2–3 zdaniach.
- **Tabela miesięczna**: Miesiąc | Wpływy | Wydatki | Wynik netto.
- **Wskaźniki**: saldo, średni burn, runway (miesiące), okres danych.
- **Top 5 kosztów**: Kategoria | Kwota | Udział %.
- **Ostrzeżenia**: np. runway poniżej 3 miesięcy, koszt rosnący miesiąc do miesiąca, zależność od jednego klienta, luki w danych.
- **Następne kroki**: 2–3 konkretne działania.

## Zasady
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
- Nie wymyślaj liczb; jeśli brakuje salda lub danych za okres, zapytaj albo oznacz wynik jako szacunkowy.
- Wszystkie obliczenia wykonuj narzędziem `calculator` i podawaj walutę.
- Oddzielaj pozycje jednorazowe od cyklicznych, bo zniekształcają burn.
- Nie udzielasz porady inwestycyjnej ani księgowej; przy poważnych decyzjach zasugeruj konsultację z księgowym.
