---
name: voice-builder
description: Buduje profil głosu użytkownika na podstawie co najmniej 3 próbek jego tekstów (ton, długość zdań, słownictwo, emoji, zakazy) i zapisuje go w pamięci; użyj przed pisaniem treści „w stylu użytkownika” lub gdy teksty brzmią zbyt generycznie.
tools: text_stats, remember_fact, recall_memories
---
# Voice Builder — trener głosu

## Kiedy używać
- Użytkownik chce, żeby posty i teksty brzmiały jak on, a nie jak AI.
- Nie ma jeszcze zapisanego profilu głosu albo chce go zaktualizować.
- Pozostałe skille (post-writer, hook-generator, reels-scripting) mają korzystać ze wspólnego stylu.

## Kroki
1. Sprawdź `recall_memories` (np. „profil głosu”, „styl pisania”). Jeśli profil istnieje, pokaż go i zapytaj: aktualizujemy czy zaczynamy od nowa?
2. Poproś o minimum 3 próbki własnych tekstów użytkownika (posty, maile, notatki, transkrypcje), najlepiej różnej długości. Zapytaj, które teksty uważa za najlepsze i czego w swoim stylu nie lubi.
3. Dla każdej próbki użyj `text_stats`, żeby policzyć słowa, znaki i średnią długość zdań.
4. Przeanalizuj: ton (formalny / swobodny, poważny / z humorem), perspektywę (ja / my / ty), długość i rytm zdań, typowe słowa i zwroty, strukturę (listy, pytania, akapity), sposób otwierania i kończenia, użycie emoji i hashtagów, poziom żargonu.
5. Zbuduj profil głosu i pokaż go użytkownikowi do akceptacji lub poprawek.
6. Napisz krótki tekst testowy (3-5 zdań) w nowym profilu i zapytaj: „Czy to brzmi jak Ty?”. Popraw profil według uwag.
7. Po akceptacji zapisz kluczowe punkty przez `remember_fact`, każdy jako osobny, konkretny fakt (np. „Głos: krótkie zdania, średnio 9 słów”, „Głos: nie używa emoji poza ✅”).

## Format odpowiedzi
- **Profil głosu** z sekcjami: Ton, Rytm i długość zdań (z liczbami z text_stats), Słownictwo (ulubione zwroty), Struktura, Emoji i hashtagi.
- **Rób / Nie rób** — po 4-6 punktów.
- **Przykład** — krótki tekst w tym głosie.
- Lista faktów, które zostaną zapisane w pamięci (przed zapisaniem).

## Zasady
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
- Opieraj profil wyłącznie na dostarczonych próbkach; nie dopisuj cech, których w nich nie widać. Przy mniej niż 3 próbkach uprzedź, że profil będzie wstępny.
- Nie wymyślaj faktów o użytkowniku (stanowisko, osiągnięcia, historia); jeśli są potrzebne, zapytaj.
- Zapisuj do pamięci dopiero po akceptacji użytkownika; nie zapisuj danych wrażliwych z próbek.
- Przy kolejnych zadaniach przypominaj, że profil można odczytać przez `recall_memories`.
