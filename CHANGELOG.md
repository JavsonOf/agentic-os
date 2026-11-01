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
Linia `> Instalacja: …` zastępuje ostatnie zdanie instrukcji instalacji („Nowa wersja instaluje się na poprzedniej.”),
np. gdy zmienił się klucz podpisu i starą aplikację trzeba najpierw odinstalować.

## Następne wydanie

### Drobne zmiany
- Skill `/scal-i-sprawdz` dla Claude Code w repozytorium (`.claude/skills/`): scala PR, gdy testy są zielone, a potem po kolei sprawdza opisy wydań i nowe wydanie.

## v0.10.0 – Formatted Replies: Lists, Tables and Code
_01.11.2026_

### Dodano
- Odpowiedzi agentów są ładnie sformatowane, zamiast pokazywać surowe znaczki Markdown (#, *, |, ```).
  - Nagłówki, listy punktowane i numerowane (także z podpunktami), cytaty i linie oddzielające.
  - Tabele z nagłówkiem, które na wąskim ekranie przewijają się w bok.
  - Bloki kodu z nazwą języka i przyciskiem „Kopiuj”, który kopiuje sam kod.
  - Klikalne linki, otwierane w nowej karcie (tylko adresy http i https).
  - Pogrubienie, kursywa i kod w tekście.
  - Formatowanie jest bezpieczne: HTML w odpowiedzi agenta pokazuje się jako zwykły tekst i nigdy się nie wykonuje.

### Ulepszono
- Podglądy odpowiedzi w sekcji „Na dziś” pokazują czysty tekst, bez znaczków formatowania.
- Powiadomienia (np. „Skopiowano”) przy otwartym oknie pojawiają się u góry ekranu, zamiast zasłaniać listę w oknie.

## v0.9.0 – Conversation History
_01.11.2026_

### Dodano
- Historia rozmów w czacie, jak w innych aplikacjach AI: przycisk „Rozmowy” w nagłówku rozmowy.
  - Lista poprzednich rozmów z agentem: tytuł z pierwszego pytania, dzień, godzina i liczba wiadomości.
  - Dotknięcie rozmowy otwiera ją z powrotem. Agent pamięta jej przebieg, dopóki serwer nie został uruchomiony ponownie.
  - Przy każdej rozmowie jest „✕”, żeby usunąć ją z historii.
  - Historia trzyma 20 ostatnich rozmów z każdym agentem, w tej przeglądarce lub aplikacji.

### Zmieniono
- „Nowa rozmowa” nie kasuje już poprzedniej rozmowy, tylko odkłada ją do historii.

## v0.8.0 – Reply Actions and One-Tap Follow-Ups
_01.11.2026_

### Dodano
- Akcje pod każdą odpowiedzią agenta w czacie: odpowiedź nie kończy już rozmowy.
  - „Kopiuj”: cała odpowiedź trafia do schowka.
  - „Udostępnij” (na telefonie): wysyłasz odpowiedź dalej, np. przez komunikator albo e-mail.
  - „Rób to codziennie”: jednym dotknięciem pytanie staje się zaplanowanym zadaniem. Formularz otwiera się z nazwą, treścią i agentem już wpisanymi, wystarczy wybrać godzinę i zapisać.
- Szybkie odpowiedzi pod ostatnią odpowiedzią agenta: „Krócej”, „Więcej szczegółów” i „W punktach” wysyłają gotową prośbę bez pisania.

## v0.7.0 – Connect AI in 60 Seconds
_01.11.2026_

### Dodano
- „Połącz AI w 60 sekund”: prowadzone podłączenie modelu AI zamiast długiego formularza. Otwiera się z przycisku „Połącz AI” na ekranie startowym i w zakładce Modele.
  - Wybór jednym dotknięciem: Google Gemini (darmowy, zalecany), OpenRouter (darmowe modele) albo Anthropic Claude.
  - Krótka instrukcja i link prosto do strony, na której tworzy się klucz.
  - Pole klucza z przyciskiem „Wklej” i podpowiedzią, gdy klucz wygląda na niepełny.
  - Klucz od razu jest sprawdzany. Po sukcesie: „Gotowe!” i przycisk „Zadaj pierwsze pytanie” z gotowym pytaniem na start.
  - Inni dostawcy (OpenAI, Groq, Ollama…) dalej są w zakładce Modele.

### Naprawiono
- Usunięcie dostawcy ustawionego jako domyślny przywraca model z ustawień serwera. Wcześniej aplikacja dalej pokazywała go jako połączony, choć nie działał.
- Klucz, który nie przeszedł sprawdzenia w „Połącz AI”, nie zostaje zapisany jako działający dostawca.

## v0.6.0 – Today Feed on the Start Screen
_01.11.2026_

### Dodano
- Sekcja „Na dziś” na ekranie startowym: od razu widać, co wymaga uwagi i co agenci zrobili, gdy Cię nie było.
  - Decyzje, na które czekają agenci, są na samej górze i prowadzą prosto do rozmowy z agentem.
  - Wyniki zaplanowanych zadań z ostatniej doby („Poranne podsumowanie – gotowe”) z fragmentem odpowiedzi. Znikają z listy, gdy je otworzysz.
  - „Kontynuuj rozmowę” z ostatnim agentem i fragmentem jego ostatniej odpowiedzi.
  - Najbliższe zaplanowane zadanie, np. „jutro o 07:30”.
  - Gdy nie masz jeszcze zaplanowanych zadań: propozycja „Niech agent pracuje, gdy śpisz”, która otwiera gotowy do zapisania formularz porannego podsumowania.
  - Sekcja nie wysyła nic do modelu AI, więc nie zużywa tokenów.

### Ulepszono
- Pole „Napisz do agenta…” na ekranie startowym jest zawsze widoczne nad dolnym menu, także gdy ekran trzeba przewinąć.

## v0.5.0 – Message Editing, Agent Screen and Token Usage Counter
_01.11.2026_

### Dodano
- Edycja wysłanej wiadomości w czacie, jak w innych aplikacjach AI.
  - Pod każdą Twoją wiadomością jest ołówek „Edytuj”: poprawiasz tekst i wysyłasz go jeszcze raz.
  - Odpowiedzi po tej wiadomości znikają z ekranu i z pamięci agenta, więc agent odpowiada tak, jakby poprzedniej wersji nie było.
  - Edycja czeka, aż agent skończy odpowiadać. Esc albo „Anuluj” zostawia wiadomość bez zmian.
- Ekran agenta: w Ty → Agenci przy każdym agencie jest przycisk „✏️ Edytuj”.
  - U góry ikona agenta, jego nazwa i model, z którego korzysta.
  - Karta „Skille” pokazuje wszystkie dostępne skille jako kafelki: dotknięcie włącza albo wyłącza skill (włączony jest zielony, z ptaszkiem).
  - Każde dotknięcie zapisuje się od razu, bez przycisku „Zapisz”. Na dole pojawia się na 5 sekund „Włączono: …” z przyciskiem „Cofnij”.
  - Przytrzymanie kafelka (albo prawy przycisk myszy) pokazuje opis skilla, jego narzędzia i instrukcje, z przyciskiem włącz/wyłącz.
  - Uprawnienia, tryb myślenia, rozmowy i zgody agenta zostają bez zmian.
- Licznik zużycia w zakładce Modele: ile poszło tokenów i ile było zapytań, bez kwot.
  - Przełącznik okresu: Dziś, 7 dni, Miesiąc.
  - Suma tokenów z podziałem na wejście i wyjście oraz wykres dzień po dniu.
  - Lista dostawców z liczbą zapytań i tokenów każdego z nich.
  - Liczenie zaczyna się od tej wersji: wcześniejsze dni pokazują 0.

### Naprawiono
- Aplikacja na Androida: aparat, mikrofon i zmiana adresu serwera działają na nowych telefonach.
  - „Skanuj kod QR z komputera” włącza aparat na żywo i sam odczytuje kod. Aplikacja pyta o dostęp do aparatu przy pierwszym użyciu. Przycisk „Zrób zdjęcie” zostaje jako zapas.
  - Przycisk mikrofonu otwiera systemowe rozpoznawanie mowy telefonu, a rozpoznany tekst trafia do pola wiadomości. Aplikacja nie potrzebuje do tego dostępu do mikrofonu.
  - Adres serwera zmienisz w zakładce Ty → Adres serwera. Działa też przy nawigacji gestami, gdzie nie da się przytrzymać przycisku Wstecz.

### Ulepszono
- Formularz zaplanowanego zadania pokazuje, kiedy zadanie uruchomi się pierwszy raz, np. „Następne uruchomienie: jutro o 07:30”.
- Gdy zmieniasz adres API dostawcy z zapisanym kluczem, pole klucza od razu prosi o wpisanie go ponownie (zapisany klucz nie jest wysyłany pod nowy adres).

## v0.4.2 – Reliability Fixes: Safe Saving, Planner, Schedules and Models
_01.11.2026_

### Naprawiono
- Ustawienia, agenci, skille, mody, harmonogram i pamięć zapisują się bezpiecznie: awaria w trakcie zapisu nie zostawia już uszkodzonego pliku.
  - Gdy jakiś plik jednak jest uszkodzony, serwer odkłada go na bok i normalnie startuje, zamiast się nie uruchamiać.
  - Urwana linia w bazie wiedzy jest pomijana, a reszta dokumentów zostaje.
- Usunięcie dostawcy modelu nie kasuje już agentów, którzy z niego korzystali: przechodzą na model domyślny.
- Planowanie celów i pracy zespołu agentów nie kończy się błędem, gdy model zwróci nietypowy plan.
- Modele zgodne z OpenAI z niższym limitem odpowiedzi (np. DeepSeek) i nowsze modele OpenAI działają: aplikacja sama dopasowuje limit po pierwszej odmowie.
- Przełączenie modelu w trakcie rozmowy (np. z Claude na Gemini) nie psuje już tej rozmowy.
- Harmonogram:
  - zmiana godziny albo ponowne włączenie zadania po jego porze nie uruchamia go od razu, tylko następnego dnia;
  - „wyłączone” wysłane jako tekst naprawdę wyłącza zadanie;
  - jeden błąd (np. pełny dysk) nie zatrzymuje już harmonogramu na stałe.
- Hasło do War Room ze spacją albo nową linią na końcu (np. z pliku .env) już nie blokuje logowania.
- Obraz Dockera ma obsługę PDF i gotowy folder na dane, więc zapisywanie działa od razu po podpięciu wolumenu.

### Ulepszono
- Więcej zadań może naraz czekać na Twoją zgodę lub odpowiedź, nie blokując czatu.
- Serwer działający długo nie zajmuje coraz więcej pamięci: pamięta ostatnie 500 zakończonych zadań.
- Bezpieczeństwo:
  - po wielu próbach z błędnym hasłem trzeba odczekać kilka minut;
  - serwery MCP uruchamiane na serwerze nie dostają jego kluczy i haseł;
  - zbyt duże albo podejrzane pliki i obliczenia są odrzucane, zamiast obciążać serwer;
  - automatyczne wdrożenie na Oracle nie zapisuje tokenu GitHuba w plikach repozytorium.
- Dokumentacja: aktualna lista funkcji serwera w README i poprawna komenda Dockera z trwałymi danymi.

## v0.4.1 – Security and Stability Fixes from the Audit
_31.10.2026_

### Naprawiono
- Lepsza ochrona serwera uruchomionego bez hasła na własnym komputerze: przyjmuje tylko prośby z tego samego komputera i odrzuca te wysłane przez inne strony internetowe.
- Klucze API nie trafią tam, gdzie nie powinny:
  - po zmianie adresu dostawcy modelu albo moda trzeba wpisać klucz ponownie, zamiast wysyłać zapisany pod nowy adres;
  - połączenie z kluczem nie idzie za przekierowaniem na inny serwer;
  - edycja dostawcy bez wpisywania klucza nie zastępuje zapisanego klucza jego zamaskowaną wersją („••••”).
- Kilku agentów może naraz zapisywać wspomnienia: wcześniej odpowiedź potrafiła przepaść z błędem, a plik pamięci mógł się uszkodzić. Pamięć zapisuje się teraz w całości albo wcale.
- Wgrywanie dokumentów do bazy wiedzy nie przerywa już agentów, którzy w tym czasie z niej korzystają.
- Nowe komunikaty o tych zabezpieczeniach są wyjaśnione po polsku w War Room.

## v0.4.0 – "Server Asleep" Screen Instead of a 404
_31.10.2026_

### Dodano
- Ekran „Serwer śpi” zamiast pustej strony z błędem 404, gdy serwer War Room nie odpowiada (np. Codespace zasnął po 30 minutach bez używania).
  - Wyjaśnia po ludzku, co się stało, i zapewnia, że agenci i dane są bezpieczne.
  - Prowadzi w 3 krokach: przycisk otwierający Codespaces, gotowe komendy do włączenia serwera z przyciskiem „Kopiuj komendy” i hasłem wpisywanym tak, żeby nie było go widać.
  - Sam sprawdza serwer co 5 sekund i od razu wraca do War Room, gdy ten wstanie. Nic nie trzeba odświeżać.
  - Działa w przeglądarce i w aplikacji na Androida, także bez internetu, w jasnym i ciemnym motywie.

## v0.3.1 – New Private Signing Key for the Android App
_19.10.2026_

> Instalacja: Przed instalacją tej wersji raz odinstaluj poprzednią, bo zmienił się klucz podpisu aplikacji. Kolejne wersje będą się już instalować na tej.

### Zmieniono
- Aplikacja na Androida jest podpisywana nowym, prywatnym kluczem, którego nie ma w repozytorium. Dzięki temu nikt poza tym projektem nie może wydać wersji, którą telefon uzna za aktualizację.
  - Przed instalacją tej wersji trzeba raz odinstalować poprzednią, bo Android nie pozwala zmienić klucza przy aktualizacji.
  - Po instalacji podaj ponownie adres serwera i hasło do War Room. Dla pewności warto przy okazji zmienić to hasło.

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
