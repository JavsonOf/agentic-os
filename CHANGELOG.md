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
- Ponowne zbudowanie tej samej wersji, bez zmian w aplikacji, dostaje metadane po plusie: `v0.2.6+build.1`
  (plik `AgenticOS_v0.2.6_build.1.apk`). Numer wersji zostaje ten sam, a dopisek mówi, że to techniczna kompilacja.
- Wersje testowe (np. żeby sprawdzić, czy nowy plik APK się instaluje) mają przyrostek po numerze:
  `v0.3.0-alpha.1` (wczesna próba), `v0.3.0-beta.1` (funkcje gotowe, szukanie błędów), `v1.0.0-rc.1`
  (kandydat na wydanie: jeśli nie ma błędów, staje się `v1.0.0`). Są oznaczone na GitHubie jako
  „Pre-release” i nigdy nie stają się „Latest”, więc zwykła instalacja ich nie pobiera.

## Jak dopisywać zmiany

Nowe zmiany dopisuj w sekcji **Następne wydanie**, w jednej z kategorii: Dodano, Zmieniono, Usunięto,
Naprawiono, Ulepszono. Scalenie takiej zmiany od razu tworzy nowe wydanie z punktami, których nie było
w poprzednim. Drobiazgi, dla których nie warto wydawać nowej wersji (literówka, kosmetyka, porządki
w kodzie, dokumentacja), wpisuj w kategorii **Drobne zmiany**: zostają zapisane i pojawią się w opisie
najbliższego prawdziwego wydania. Nowa wersja aplikacji na Androida zawsze dostaje wydanie.

Opisy są rozszerzone: gdy zmiana obejmuje kilka elementów (agentów, skille, ekrany, funkcje), wypisz każdy
jako podpunkt z wcięciem (`  - …`) i krótkim opisem, co robi. Podpunkty trafiają do opisu wydania.

W linii `Tytuł:` wpisz po angielsku krótki opis najważniejszej zmiany (Title Case, np. „QR Code Pairing”). Numer wersji automat wylicza sam
(MINOR, gdy jest coś w Dodano, inaczej PATCH). Linię `Wersja: major` albo `Wersja: minor` dopisz tylko wtedy,
gdy ten automatyczny skok jest za mały. Dla wersji testowej dopisz w tej samej linii `alpha`, `beta` albo `rc`.
Linia `Wersja: alpha`, `Wersja: beta` albo `Wersja: rc` robi z wydania wersję testową następnego numeru
(`v0.3.0-beta.1`, przy kolejnym scaleniu `v0.3.0-beta.2`), a `Wersja: major rc` daje `v1.0.0-rc.1`. Gdy usuniesz
tę linię, następne scalenie wyda wersję stabilną z tym samym numerem (`v0.3.0`). Linia `Wersja: build` od razu
buduje ostatnią wersję od nowa jako `v0.2.6+build.1`.

Pod nagłówkiem wydanej wersji możesz dopisać linię `> Uwaga: …`. Pojawi się w opisie tego wydania na GitHubie.

## Następne wydanie

### Drobne zmiany
- Opisy wydań są rozszerzone: gdy zmiana obejmuje kilka elementów (np. agentów i ich skille), każdy jest wypisany jako podpunkt.

## v0.3.0 – Ready-Made Team of 5 Agents with 25 Skills
_19.10.2026_

### Dodano
- Gotowy zespół: 5 agentów, każdy z 5 skillami ze swojej działki. Dodajesz ich jednym przyciskiem w Ty → Agenci → 📦 Gotowy zespół. Korzystają z modelu domyślnego.
  - 🏪 **Mała firma** (`mala-firma`): przepływy pieniężne (Cash Flow Snapshot), kampania sprzedażowa (Run Campaign), przygotowanie do podatków (Tax Prep), plan wypłat (Plan Payroll), windykacja zaległych faktur (Invoice Chase).
  - 📱 **Social media** (`social-media`): posty na LinkedIn i inne (Post Writer), nauka Twojego stylu pisania (Voice Builder), chwytliwe pierwsze zdania (Hook Generator), scenariusze rolek i shortów (Reels Scripting), poprawa profilu (Profile Optimizer).
  - 💻 **Programista** (`programista`): uporządkowana praca nad kodem: plan, testy, debugowanie, przegląd (Superpowers), pamięć projektu (Memory Keeper), tworzenie nowych skilli (Skill Creator), budowa serwerów MCP (MCP Builder), aktualna dokumentacja bibliotek, także przez Context7 (Docs Fetcher).
  - 🎨 **Projektant** (`projektant`): pełny system UI/UX (UI UX Pro Max), księga marki (Brand Guidelines), prototypy stron w jednym pliku HTML (Web Artifacts), kod front-endu (Frontend Design), krytyka designu z oceną i poprawkami (Taste).
  - 📣 **Marketing** (`marketing`): teksty sprzedażowe (Copywriting), materiały za zapis na listę (Lead Magnets), analiza opinii klientów (Customer Research), zwiększanie konwersji (CRO), widoczność w wyszukiwarkach AI i Google (AI SEO).
- Skille są napisane po polsku specjalnie dla Agentic OS. Agenci nie podają z pamięci stawek ani terminów podatkowych i nie wymyślają liczb ani opinii.

## v0.2.8 – Clear Notice When No AI Model Is Set
_18.10.2026_

### Ulepszono
- Gdy agent nie ma ustawionego modelu AI, jego odpowiedź zaczyna się od jasnej uwagi po polsku, że to tryb testowy bez AI, i mówi, gdzie ustawić model. Wcześniej pokazywał niezrozumiały tekst po angielsku.

## v0.2.7 – Clear OpenRouter Privacy Errors
_18.10.2026_

### Ulepszono
- War Room wyjaśnia po polsku dwa częste błędy OpenRoutera i podaje, co zmienić:
  - brak dostawcy modelu zgodnego z Twoimi ustawieniami prywatności (np. ZDR), z linkiem do tych ustawień;
  - model, który nie obsługuje narzędzi używanych przez agenta.

### Drobne zmiany
- Zmiana samej instrukcji aplikacji na Androida nie tworzy już nowego wydania.
- Ponowne zbudowanie tej samej wersji dostaje dopisek po plusie, np. v0.2.6+build.1, a wydanie może mieć w opisie własną uwagę.

## v0.2.6 – Versioned APK File Names & Test Builds
_15.10.2026_

> Uwaga: To wydanie powstało automatycznie po zmianach w automatyzacji wydań i w instrukcji instalacji. Aplikacja jest taka sama jak w v0.2.5, zmienił się tylko numer wersji pokazywany w ustawieniach Androida i nazwa pliku. Nie musisz jej aktualizować.

### Zmieniono
- Plik aplikacji w każdym wydaniu ma w nazwie numer wersji, np. AgenticOS_v0.2.6.apk. W starszych wydaniach zmieniła się tylko nazwa pliku, sam plik jest ten sam.
- Można wydawać wersje testowe alpha, beta i rc (np. v0.3.0-beta.1) oznaczone jako „Pre-release”.
- Wydania sprzed zmiany numeracji mają w opisie uwagę, że ich aplikacja pokazuje dawny numer wersji zapisany w pliku APK.

## v0.2.5 – Semantic Versioning & Readable Release Titles
_15.10.2026_

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
