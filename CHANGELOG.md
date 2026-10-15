# Co nowego w Agentic OS

Opisy zmian do każdego wydania na GitHubie (zakładka **Releases**). Są celowo ogólne: mówią, co się
zmieniło dla użytkownika, ale nie podają szczegółów technicznych, adresów, kluczy ani opisów luk, które
mogłyby komuś pomóc w ataku.

## Wersje i nazwy wydań

- Każde wydanie ma numer w formacie SemVer `vMAJOR.MINOR.PATCH`, teraz `v0.MINOR.PATCH`. Numery idą po kolei,
  bez przeskoków, i nie zależą od numerów budowania ani PR.
- **MAJOR** (`v0.x.x` → `v1.0.0`): pierwsze stabilne wydanie albo zmiana, która psuje zgodność z poprzednią wersją.
- **MINOR** (`v0.2.0` → `v0.3.0`): nowe funkcje, ekrany i integracje, czyli punkty w kategorii **Dodano**.
- **PATCH** (`v0.2.0` → `v0.2.1`): poprawki błędów, ulepszenia, zmiany w automatyzacji i dokumentacji.
- Tytuł wydania jest po angielsku, bo repozytorium jest publiczne: `vX.Y.Z – Krótki opis najważniejszej zmiany`,
  np. `v0.2.1 – Clear Connection Errors in the Android App`. Bez „Agentic OS” i „Release”. Opisy zmian
  zostają po polsku.
- Wersje testowe, gdyby były potrzebne: `v0.3.0-beta.1`, `v1.0.0-rc.1`.

## Jak dopisywać zmiany

Nowe zmiany dopisuj w sekcji **Następne wydanie**, w jednej z kategorii: Dodano, Zmieniono, Usunięto,
Naprawiono, Ulepszono. Scalenie takiej zmiany od razu tworzy nowe wydanie z punktami, których nie było
w poprzednim. Drobiazgi, dla których nie warto wydawać nowej wersji (literówka, kosmetyka, porządki
w kodzie, dokumentacja), wpisuj w kategorii **Drobne zmiany**: zostają zapisane i pojawią się w opisie
najbliższego prawdziwego wydania. Nowa wersja aplikacji na Androida zawsze dostaje wydanie.

W linii `Tytuł:` wpisz po angielsku krótki opis najważniejszej zmiany (Title Case, np. „QR Code Pairing”). Numer wersji automat wylicza sam
(MINOR, gdy jest coś w Dodano, inaczej PATCH). Linia `Wersja: major` albo `Wersja: minor` wymusza inny skok.

## Następne wydanie

Tytuł: Semantic Versioning & Readable Release Titles

### Zmieniono
- Wydania mają numery wersji w formacie v0.X.Y i krótkie angielskie tytuły, np. „v0.2.1 – Clear Connection Errors in the Android App”. Wcześniejsze wydania dostały nowe numery i nazwy według tej samej zasady.

## v0.2.4 – Bilingual Release Names
_15.10.2026 · dawniej android-16_

### Zmieniono
- Nazwy wydań na GitHubie są teraz po polsku i angielsku, np. „Agentic OS – wydanie 14 · Release 14”.

## v0.2.3 – A Release for Every Important Change
_15.10.2026 · dawniej android-14_

### Zmieniono
- Nowe wydanie powstaje po każdej ważnej zmianie w Agentic OS, a nie tylko po zmianach w aplikacji na Androida. Drobiazgi trafiają do opisu najbliższego wydania zamiast tworzyć osobne.

## v0.2.2 – Release Notes in Polish
_15.10.2026 · dawniej android-11_

### Dodano
- Każde wydanie na GitHubie ma teraz opis po polsku: co dodano, co zmieniono, co usunięto, jakie błędy naprawiono i co ulepszono.

## v0.2.1 – Clear Connection Errors in the Android App
_15.10.2026 · dawniej android-9_

### Ulepszono
- Aplikacja na Androida nie pokazuje już technicznych kodów błędów. Gdy coś nie działa, widać krótkie wyjaśnienie po polsku, np. brak internetu, serwer wyłączony albo zły adres.
- Ekran błędu ma przyciski „Spróbuj ponownie” i „Zmień adres serwera” oraz pasuje do jasnego i ciemnego motywu telefonu.
- Okno adresu serwera samo poprawia częste literówki i mówi wprost, co jest nie tak z wpisanym adresem.

### Naprawiono
- Aplikacja rozpoznaje, gdy serwer w chmurze jest uśpiony lub wyłączony, i mówi o tym zamiast pokazywać pustą stronę.
- Adres zapisany w starszej wersji, który nie może działać, nie blokuje już aplikacji: przy starcie pojawia się prośba o poprawny.

## v0.2.0 – Redesigned War Room, Recurring Tasks & Knowledge Files
_15.10.2026 · dawniej android-8_

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

## v0.1.0 – First Release of Agentic OS & the Android App
_15.10.2026 · dawniej android-2_

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
