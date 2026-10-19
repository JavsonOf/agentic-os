---
name: skill-creator
description: Kowal Skilli: przeprowadza wywiad i tworzy gotowy plik SKILL.md dla Agentic OS do wklejenia w War Room. Użyj, gdy użytkownik chce stworzyć nowy skill lub poprawić istniejący.
---
# Kowal Skilli – tworzenie skilli dla Agentic OS

## Kiedy używać
- Użytkownik chce „nauczyć” agenta powtarzalnej procedury lub stylu pracy.
- Istniejący skill działa słabo i trzeba poprawić jego opis lub instrukcje.

## Kroki
1. **Wywiad (3–6 pytań, po kolei):** jakie zadanie ma wykonywać skill? Kiedy agent powinien go użyć, a kiedy nie? Jakie są kroki procedury? Jaki ma być format wyniku? Jakie są zakazy lub pułapki? Których narzędzi będzie potrzebował?
2. **Nazwa:** krótka, z małych liter, tylko znaki `a-z A-Z 0-9 _ -`, maksymalnie 64 znaki (np. `faktury-kontrola`).
3. **Opis:** jedno zdanie mówiące, co skill robi i kiedy go użyć. Agenci widzą w katalogu wyłącznie nazwę i opis, a pełną treść ładują dopiero przez `load_skill` – dlatego opis musi być konkretny. Zły: „Pomaga z dokumentami”. Dobry: „Sprawdza faktury VAT pod kątem brakujących pól i błędów w sumach; użyj, gdy użytkownik wkleja fakturę”.
4. **Narzędzia (opcjonalnie):** wybierz tylko spośród dostępnych: calculator, csv_summary, text_stats, search_knowledge, recall_memories, remember_fact (oraz narzędzia MCP, jeśli użytkownik je podłączył).
5. **Treść:** markdown z sekcjami „Kiedy używać”, „Kroki”, „Format odpowiedzi”, „Zasady”. Pisz w trybie rozkazującym, konkretnie, bez lania wody. Pamiętaj, że agenci nie mają powłoki, plików ani przeglądarki.
6. **Pokaż szkic** i zapytaj o poprawki, zanim podasz wersję końcową.

## Format odpowiedzi
Podaj cały plik w jednym bloku kodu (oznacz go jako `markdown`), według wzoru:
- linia `---`
- `name: nazwa-skilla`
- `description: jedno zdanie – co robi i kiedy go użyć`
- `tools: calculator, search_knowledge` (linię można pominąć)
- linia `---`
- tytuł `# ...` i treść w markdownie

Na końcu instrukcja: „Wklej to w War Room: **Ty → Skille** (sekcja skilli), zapisz, a potem przypisz skill wybranemu agentowi”.

## Zasady
- Jeden skill = jedno zadanie; zbyt szeroki pomysł podziel na kilka skilli.
- Nie wpisuj do skilla sekretów ani kluczy API.
- Odpowiadaj w języku użytkownika (domyślnie po polsku).
