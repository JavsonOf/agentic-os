---
name: customer-research
description: Syntetyzuje głos klienta z opinii, wywiadów, ankiet i zgłoszeń supportu (tekst, CSV lub baza wiedzy) w tematy, JTBD, bóle, obiekcje i segmenty; użyj przed pisaniem komunikacji, pozycjonowaniem lub planowaniem produktu.
tools: csv_summary, text_stats, search_knowledge, recall_memories, remember_fact
---
# Badanie klientów (Voice of Customer)

## Kiedy używać
- Masz zbiór opinii, transkrypcji wywiadów, odpowiedzi z ankiet lub zgłoszeń i chcesz z nich wyciągnąć wnioski.
- Przygotowujesz copy, pozycjonowanie lub roadmapę i potrzebujesz języka klientów.
- Chcesz zrozumieć, dlaczego ludzie kupują, rezygnują lub się wahają.

## Kroki
1. **Źródła.** Ustal, skąd pochodzą dane (opinie, wywiady, ankiety, tickety), jaki okres obejmują i ile ich jest. Dane mogą być wklejone, w CSV (użyj `csv_summary`) lub w bazie wiedzy (`search_knowledge`). Długość i częstotliwość słów sprawdzaj przez `text_stats`.
2. **Kodowanie.** Przeczytaj wypowiedzi i przypisz im etykiety: ból, pożądany wynik, wyzwalacz zakupu, obiekcja, alternatywa, pochwała.
3. **Tematy.** Pogrupuj etykiety w 5–10 tematów; przy każdym podaj liczbę wystąpień tylko wtedy, gdy faktycznie je policzono.
4. **Jobs-to-be-done.** Sformułuj zadania w formie: „Kiedy [sytuacja], chcę [motywacja], aby [oczekiwany wynik]”.
5. **Cytaty.** Wybierz dosłowne cytaty (bez poprawiania) ilustrujące każdy temat, ze wskazaniem źródła.
6. **Obiekcje i segmenty.** Wypisz główne obawy przed zakupem oraz segmenty różniące się potrzebami lub kontekstem.
7. **Wnioski.** Przełóż ustalenia na rekomendacje dla marketingu, sprzedaży i produktu.

## Format odpowiedzi
- Krótkie podsumowanie danych (źródła, liczba rekordów, ograniczenia próby).
- Tabela insightów: Temat | Opis | Częstość | Przykładowy cytat | Źródło | Implikacja.
- Lista JTBD, bólów, pożądanych wyników i obiekcji.
- Opis 2–4 segmentów.
- „Słownik klienta”: frazy do wykorzystania w copy.
- Pytania otwarte i propozycje dalszych badań.

## Zasady
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
- Cytaty muszą być dosłowne i pochodzić z dostarczonych danych — nigdy ich nie wymyślaj ani nie „ulepszaj”.
- Oddzielaj fakty (co powiedzieli klienci) od interpretacji (co z tego wnioskujesz).
- Przy małej próbie wyraźnie zaznacz, że wnioski są wstępne.
- Anonimizuj dane osobowe w cytatach.
- Kluczowe insighty i segmenty zapisz przez `remember_fact`.
