---
name: invoice-chase
description: Pomaga odzyskać zaległe płatności — wypisuje przeterminowane faktury, ustala priorytety i przygotowuje eskalujące wezwania (uprzejme przypomnienie, stanowcze wezwanie, ostateczne wezwanie); użyj, gdy klienci spóźniają się z zapłatą.
tools: csv_summary, calculator, recall_memories, remember_fact
---
# Windykacja faktur

## Kiedy używać
- Użytkownik ma listę niezapłaconych faktur (CSV lub wklejoną) i chce wiedzieć, od czego zacząć.
- Trzeba napisać przypomnienie lub wezwanie do zapłaty w odpowiednim tonie.
- Przy cotygodniowym przeglądzie należności.

## Kroki
1. Sprawdź `recall_memories`: historia kontaktów z danym klientem, wcześniej wysłane przypomnienia, ustalenia.
2. Jeśli dane są w CSV, użyj `csv_summary`. Potrzebne pola: klient, numer faktury, kwota, termin płatności. Zapytaj o dzisiejszą datę, jeśli nie jest znana, oraz o brakujące pola.
3. Policz `calculator`em liczbę dni po terminie i sumę zaległości na klienta.
4. Ustal priorytety: najpierw wysoka kwota i długie opóźnienie, potem klienci z wieloma zaległymi fakturami; uwzględnij wagę relacji.
5. Przypisz etap: do ok. 7 dni — uprzejme przypomnienie; dłużej — stanowcze wezwanie; po braku reakcji — ostateczne wezwanie z zapowiedzią dalszych kroków.
6. Przygotuj treści wiadomości dla każdego etapu, z danymi faktury i jasnym terminem zapłaty.
7. Zaproponuj zapisanie wysłanych etapów i obietnic zapłaty przez `remember_fact`.

## Format odpowiedzi
- **Tabela zaległości**: Klient | Faktura | Kwota | Dni po terminie | Etap | Priorytet.
- **Suma zaległości** łącznie i na klienta.
- **Szkice wiadomości**: temat i treść dla każdego etapu (uprzejmy → stanowczy → ostateczny).
- **Plan działań** na najbliższy tydzień.

## Zasady
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
- Nie wymyślaj kwot, dat ani numerów faktur; brakujące dane oznacz `[do uzupełnienia]`.
- Ton zawsze profesjonalny, bez gróźb i nacisku emocjonalnego, także w ostatecznym wezwaniu.
- Możesz wspomnieć o prawie do odsetek ustawowych za opóźnienie i rekompensaty za koszty odzyskiwania należności, ale bez podawania stawek i kwot — użytkownik musi je zweryfikować.
- Nie wysyłasz wiadomości samodzielnie; przygotowujesz je do wysłania przez użytkownika.
- Przy dużych kwotach lub sporze zasugeruj konsultację z prawnikiem.
