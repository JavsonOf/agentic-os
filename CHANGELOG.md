# Co nowego w Agentic OS

Opisy zmian do każdego wydania na GitHubie (zakładka **Releases**). Są celowo ogólne: mówią, co się
zmieniło dla użytkownika, ale nie podają szczegółów technicznych, adresów, kluczy ani opisów luk, które
mogłyby komuś pomóc w ataku.

Nowe zmiany dopisuj w sekcji **Następne wydanie**, w jednej z kategorii: Dodano, Zmieniono, Usunięto,
Naprawiono, Ulepszono. Każda scalona zmiana tworzy nowe wydanie, a automat sam wybiera do niego punkty,
których nie było w poprzednim.

## Następne wydanie

### Dodano
- Każde wydanie na GitHubie ma teraz opis po polsku: co dodano, co zmieniono, co usunięto, jakie błędy naprawiono i co ulepszono.

### Zmieniono
- Nowe wydanie powstaje po każdej zmianie w Agentic OS, a nie tylko po zmianach w aplikacji na Androida.

## android-9 · 15.10.2026

### Ulepszono
- Aplikacja na Androida nie pokazuje już technicznych kodów błędów. Gdy coś nie działa, widać krótkie wyjaśnienie po polsku, np. brak internetu, serwer wyłączony albo zły adres.
- Ekran błędu ma przyciski „Spróbuj ponownie” i „Zmień adres serwera” oraz pasuje do jasnego i ciemnego motywu telefonu.
- Okno adresu serwera samo poprawia częste literówki i mówi wprost, co jest nie tak z wpisanym adresem.

### Naprawiono
- Aplikacja rozpoznaje, gdy serwer w chmurze jest uśpiony lub wyłączony, i mówi o tym zamiast pokazywać pustą stronę.
- Adres zapisany w starszej wersji, który nie może działać, nie blokuje już aplikacji: przy starcie pojawia się prośba o poprawny.

## android-8 · 15.10.2026

### Dodano
- Nowy wygląd War Room (wersja C) z jasnym, ciemnym i systemowym motywem oraz czterema kolorami akcentu.
- Dolny pasek z pięcioma zakładkami: Czat, Zadania, Wiedza, Modele i Ty.
- Ekran startowy czatu z kartami agentów i „Szybkimi zadaniami”, a w przeglądarkach, które to obsługują, wpisywanie głosem.
- Prośby agenta o zgodę i jego pytania pojawiają się w rozmowie, z czasem, jaki został na odpowiedź.
- Zadania cykliczne: agent może sam wykonywać zadanie codziennie, w dni robocze albo w weekendy o wybranej godzinie.
- Pasek postępu dla zadań w toku i podgląd gotowych odpowiedzi.
- Wiedza: wgrywanie plików PDF, DOCX, TXT i MD, wyszukiwanie w treści dokumentów i usuwanie ich.
- Modele: licznik dzisiejszych zapytań z opcjonalnym dziennym limitem, lista modeli prosto od dostawcy i informacja, czy klucz działa.
- Powiadomienia o prośbach agenta, gdy aplikacja jest w tle (w przeglądarkach, które to obsługują).
- Logowanie telefonu przez kod QR wyświetlany na komputerze.
- Wybór modelu z listy zamiast wpisywania nazwy ręcznie.
- Ostrzeżenie w czacie, gdy nie ustawiono żadnego modelu AI.

### Zmieniono
- Rzadziej używane sekcje (Agenci, Rozszerzenia, Monitoring) przeniesiono do zakładki Ty, a Mózg i import pamięci do zakładki Wiedza.

### Ulepszono
- Każdy błąd, który może się pojawić, jest wyjaśniony prostym językiem po polsku, z podpowiedzią, co zrobić dalej. Pełna treść błędu jest dostępna pod „Szczegóły”.
- Przy chwilowym przeciążeniu dostawcy modelu aplikacja sama próbuje ponownie, zanim pokaże błąd.

### Naprawiono
- Odpowiedź agenta nie ginie już po zerwaniu połączenia, przeładowaniu strony czy zamknięciu karty: rozmowa wraca, a odpowiedź pojawia się, gdy będzie gotowa.
- Błędny komunikat „Failed to fetch” w czacie, gdy odpowiedź była już gotowa w Zadaniach.
- Nieczytelny tekst złożony z powtórzonych słów „null” w szczegółach zadania.

## android-2 · 15.10.2026

### Dodano
- Pierwsze wydanie aplikacji Agentic OS na Androida: War Room w aplikacji, która łączy się z Twoim serwerem.
- Agentic OS: agenci AI z narzędziami, pamięcią, bazą wiedzy, planowaniem i uczeniem się z ocen.
- War Room: aplikacja w przeglądarce do rozmów z agentami, zarządzania nimi i podglądu ich pracy, z możliwością instalacji na telefonie.
- Obsługa modeli Gemini, Claude oraz dostawców zgodnych z OpenAI, a także agentów zewnętrznych, serwerów MCP, skilli i własnych narzędzi.
- Uprawnienia agentów: od „zawsze pytaj” po pełną samodzielność, z możliwością zmiany w każdej chwili.
- Import pamięci z innych asystentów AI.
- Instrukcja uruchomienia na darmowym serwerze w chmurze oraz plik z instrukcjami dla asystentów AI, które budują i aktualizują projekt.

### Ulepszono
- Gemini działa także bez dodatkowej biblioteki Google, więc instalacja jest prostsza.

### Naprawiono
- Rzadki problem z zapisem ustawień, gdy kilka rzeczy zapisywało się jednocześnie.
