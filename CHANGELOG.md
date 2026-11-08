# Co nowego w Agentic OS

Opisy zmian do każdego wydania na GitHubie (zakładka **Releases**). Są celowo ogólne: mówią, co się
zmieniło dla użytkownika, ale nie podają szczegółów technicznych, adresów, kluczy ani opisów luk, które
mogłyby komuś pomóc w ataku.

## Wersje i nazwy wydań

- Każde wydanie ma numer w formacie SemVer `vMAJOR.MINOR.PATCH`, teraz `v0.MINOR.PATCH`. Numery idą po kolei,
  bez przeskoków, i nie zależą od numerów budowania ani PR.
- **PATCH** (`v0.2.0` → `v0.2.1`), domyślnie: poprawki błędów, ulepszenia, wygląd, automatyzacja, dokumentacja
  i drobne nowości (także punkty w kategorii **Dodano**).
- **MINOR** (`v0.2.0` → `v0.3.0`), tylko z linią `Wersja: minor`: wyraźnie nowa, większa funkcja, np. nowy ekran,
  nowa integracja albo nowy sposób pracy z agentami.
- **MAJOR** (`v0.x.x` → `v1.0.0`), tylko z linią `Wersja: major`: fundamentalna, ogromna zmiana, pierwsze stabilne
  wydanie albo zmiana, która psuje zgodność z poprzednią wersją.
- Wydania od v0.7.0 do v0.14.0 dostały 02.11.2026 nowe numery według tej zasady (np. v0.14.0 to teraz v0.8.0).
  Pod nagłówkiem takiego wydania jest linia „przenumerowane z …”, a strona wydania na GitHubie wyjaśnia zmianę.
- Tytuł wydania jest po angielsku, bo repozytorium jest publiczne: `vX.Y.Z – Krótki opis najważniejszej zmiany`,
  np. `v0.2.1 – Clear Connection Errors in the Android App`. Bez „Agentic OS” i „Release”. Strona wydania na
  GitHubie jest po angielsku, a potem po polsku. Punkty w tym pliku zostają po polsku i są źródłem obu wersji.
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

Do tego samego wydania dopisz angielskie lustro, którego skrypt używa na stronie GitHuba: `#### EN Highlights`
(jedno albo dwa zdania), a potem tylko te sekcje, w których coś jest: `#### EN New Features`, `#### EN Improvements`,
`#### EN Bug Fixes`, `#### EN Docs & CI`. Po polsku dopisz `#### PL Tytuł` (krótki tytuł strony) i `#### PL Najważniejsze`.
Reszta polskiej strony bierze się z punktów powyżej. Nie pisz tu o kluczach, hasłach, tokenach, podpisie ani adresach.

W linii `Tytuł:` wpisz po angielsku krótki opis najważniejszej zmiany (Title Case, np. „QR Code Pairing”). Numer wersji automat wylicza sam
i domyślnie podnosi PATCH. Linię `Wersja: minor` dopisz przy większej nowej funkcji, a `Wersja: major` tylko
przy fundamentalnej, ogromnej zmianie. Dla wersji testowej dopisz w tej samej linii `alpha`, `beta` albo `rc`.
Linia `Wersja: alpha`, `Wersja: beta` albo `Wersja: rc` robi z wydania wersję testową następnego numeru
(`v0.3.0-beta.1`, przy kolejnym scaleniu `v0.3.0-beta.2`), a `Wersja: major rc` daje `v1.0.0-rc.1`. Gdy usuniesz
tę linię, następne scalenie wyda wersję stabilną z tym samym numerem (`v0.3.0`). Linia `Wersja: build` od razu
buduje ostatnią wersję od nowa jako `v0.2.6+build.1`.

Pod nagłówkiem wydanej wersji możesz dopisać linię `> Uwaga: …` i angielską `> Note: …`. Pojawią się w opisie
tego wydania na GitHubie. Linia `> Instalacja: …` i angielska `> Install: …` zastępują ostatnie zdanie instrukcji
instalacji („Nowa wersja instaluje się nad poprzednią.”), np. gdy starą aplikację trzeba najpierw odinstalować.

## Następne wydanie

### Drobne zmiany
- Opisy wydań na GitHubie są po angielsku i po polsku, w stałych sekcjach: najważniejsze, nowości, ulepszenia, poprawki oraz dokumentacja i CI.

#### PL Tytuł
Dwujęzyczne opisy wydań

#### PL Najważniejsze
Opisy wydań na GitHubie są po angielsku i po polsku, w tych samych sekcjach.

#### EN Highlights
GitHub release pages are in English and then in Polish, with the same sections every time.

#### EN Docs & CI
- GitHub releases are written in English and in Polish, with fixed sections: highlights, new features, improvements, bug fixes, and docs and CI.

## v0.8.5 – Gemini Works Again After Google Library Update
_07.11.2026_

### Naprawiono
- Gemini znowu odpowiada po aktualizacji biblioteki Google do wersji 3.0. Nowa wersja łączyła się z inną wersją API, w której nie ma domyślnego modelu, więc każde zapytanie kończyło się błędem, że model nie istnieje.

#### PL Tytuł
Gemini znów działa po aktualizacji biblioteki Google

#### PL Najważniejsze
Gemini znowu odpowiada po aktualizacji biblioteki Google do wersji 3.0.

#### EN Highlights
Gemini answers again after the Google library update to version 3.0.

#### EN Bug Fixes
- Gemini answers again after the Google library update to version 3.0. The new library talked to a different API version that has no default model, so every request failed because the model did not exist.


## v0.8.4 – Safer Android App and Release Builds
_07.11.2026_

### Naprawiono
- Aplikacja na Androida jest bezpieczniejsza.
  - Traktuje jako War Room tylko strony z dokładnie tego samego adresu serwera (ten sam protokół, host i port). Inna usługa na tym samym komputerze albo wersja bez https nie dostaje kamery ani mikrofonu.
  - Linki do takich stron otwierają się w przeglądarce, a nie w aplikacji.

### Drobne zmiany
- Bezpieczniejsze automatyczne buildy.
  - Testowe buildy aplikacji z pull requestów nie są oznaczane tak jak wydania.
  - Testy na prawdziwych modelach uruchamiają się tylko na gałęzi main.

#### PL Tytuł
Bezpieczniejsza aplikacja na Androida i buildy wydań

#### PL Najważniejsze
Aplikacja na Androida uznaje za War Room tylko stronę z dokładnie tego samego adresu serwera.

#### EN Highlights
The Android app treats a page as the War Room only when it is exactly your server.

#### EN Bug Fixes
- The Android app is safer.
  - It treats a page as the War Room only when the protocol, host and port are exactly the server's. Another service on the same computer, or a copy without https, does not get the camera or the microphone.
  - Links to those pages open in the browser, not in the app.

#### EN Docs & CI
- Safer automatic builds.
  - Pull-request builds are not marked the way releases are.
  - Tests that call real models run only on the main branch.


## v0.8.3 – Safer War Room and Agent Approvals
_05.11.2026_

### Naprawiono
- War Room jest bezpieczniejszy po audycie bezpieczeństwa.
  - Obcy, którzy zgadują dane logowania, nie blokują już dostępu właścicielowi, gdy serwer stoi za Caddy.
  - Serwer zamyka połączenia, przez które nic nie przychodzi, i nie da się go nimi zapchać.
  - Inna strona nie może pokazać War Room w ramce i podstępem wywołać kliknięć.
  - Kod QR do połączenia telefonu przyjmuje tylko zwykłe adresy stron.
- Agent w trybie „smart” pyta o zgodę, zanim przekaże zadanie agentowi zewnętrznemu.
- Serwer MCP nie może przejąć narzędzia innego serwera o podobnej nazwie. Taki serwer dostaje komunikat, żeby zmienić nazwę.
- Import pamięci z pliku ZIP pomija archiwa ukryte w środku archiwum, więc limit rozmiaru dotyczy całego importu.

#### PL Tytuł
Bezpieczniejszy War Room i zgody agentów

#### PL Najważniejsze
War Room jest bezpieczniejszy po audycie, a agent pyta, zanim przekaże zadanie na zewnątrz.

#### EN Highlights
The War Room is safer after the audit, and an agent asks before handing a task to an external agent.

#### EN Bug Fixes
- The War Room is safer after a security audit.
  - People guessing the login no longer lock the owner out when the server sits behind Caddy.
  - The server closes connections that send nothing, so they cannot be used to fill it up.
  - Another site cannot show the War Room in a frame and trick you into clicking.
  - The QR code that connects a phone accepts only ordinary web addresses.
- In “smart” mode an agent asks before it hands a task to an external agent.
- An MCP server cannot take over another server's tool with a similar name. That server is told to rename it.
- Importing memory from a ZIP skips archives hidden inside the archive, so the size limit covers the whole import.


## v0.8.2 – Live View of What the Agent Is Doing
_04.11.2026_

### Ulepszono
- Gdy agent pracuje, zamiast samego „Myślę…” widać na żywo, co właśnie robi.
  - Każdy krok to jedna linia po polsku, np. „🔎 Szukam w wiedzy „plan na tydzień””, „🧮 Liczę „8*5””, „🌐 Sprawdzam w internecie”.
  - Bieżący krok jest wyróżniony, a skończone są przygaszone.
  - Obok widać, od ilu sekund agent pracuje.
- „Zatrzymaj” zatrzymuje agenta także tuż przed użyciem narzędzia, nie tylko przed kolejnym krokiem modelu.

### Drobne zmiany
- Skaner bezpieczeństwa CodeQL sprawdza kod serwera, aplikacji webowej, aplikacji na Androida i automatyzacji przy każdej zmianie i co tydzień. Wyniki są w zakładce Security repozytorium.
- Opisy przenumerowanych wydań (v0.6.1–v0.8.0) mówią osobną linią, że aplikacja może w ustawieniach Androida pokazywać stary numer wersji, np. 0.13.0.

#### EN Tytuł
Live view of what the agent is doing

#### PL Tytuł
Na żywo widać, co robi agent

#### EN Highlights
While an agent works you now see, live, what it is doing — instead of just "Thinking…". (#49)

#### EN Improvements
- **Live agent activity view** — each step is one line, e.g. "🔎 Searching knowledge for "plan na tydzień"", "🧮 Calculating "8*5"", "🌐 Checking the web". (#49)
  - The current step is highlighted, finished steps are dimmed.
  - A timer shows how many seconds the agent has been working.
- **Stop works earlier** — "Zatrzymaj" now stops the agent right before a tool call, not only before the next model step. (#49)

#### EN Bug Fixes
- Anchored the `ask_` tool-name pattern correctly in the UI (ee90170, #49).

#### EN Docs & CI
- CodeQL security scanning for the server, web app, Android app and automation on every change and weekly; results in the repo's Security tab. (#50)
- Renumbered releases (v0.6.1–v0.8.0) state on a separate line that Android settings may still show the old version number, e.g. 0.13.0. (#48)

#### PL Najważniejsze
Gdy agent pracuje, widzisz na żywo, co robi — zamiast samego „Myślę…”. (#49)

#### PL Ulepszenia
- **Podgląd aktywności agenta na żywo** — każdy krok to jedna linia, np. „🔎 Szukam w wiedzy: plan na tydzień”, „🧮 Liczę 8*5”, „🌐 Sprawdzam w sieci”. (#49)
  - Aktualny krok jest podświetlony, skończone są przygaszone.
  - Timer pokazuje, ile sekund agent już pracuje.
- **Zatrzymaj działa wcześniej** — „Zatrzymaj” przerywa agenta tuż przed wywołaniem narzędzia, a nie dopiero przed kolejnym krokiem modelu. (#49)

#### PL Poprawki
- Poprawione zakotwiczenie wzorca nazw narzędzi `ask_` w UI (ee90170, #49).

#### PL Dokumentacja i CI
- Skanowanie bezpieczeństwa CodeQL dla serwera, aplikacji webowej, Androida i automatyzacji przy każdej zmianie oraz co tydzień; wyniki w zakładce Security w repo. (#50)
- Przy przenumerowanych wydaniach (v0.6.1–v0.8.0) osobna linia informuje, że ustawienia Androida mogą nadal pokazywać stary numer wersji, np. 0.13.0. (#48)

## v0.8.1 – Messages That Wait for the Network
_02.11.2026_

### Dodano
- Wiadomości bez internetu nie przepadają. Gdy napiszesz do agenta bez połączenia, wiadomość czeka w czacie z napisem „Brak połączenia” i wysyła się sama, gdy wróci sieć.
  - Działa też po zamknięciu i ponownym otwarciu aplikacji.
  - Kilka czekających wiadomości wysyła się po kolei, a po wysłaniu pojawia się krótki komunikat.
- Wiesz, kiedy odpowiedź jest gotowa, nawet gdy aplikacja jest w tle.
  - W tytule karty widać liczbę nowych odpowiedzi, np. „(2) Agentic OS”. Licznik znika po powrocie do aplikacji.
  - Z włączonymi powiadomieniami telefon pokazuje początek odpowiedzi albo informację, że zadanie się nie udało.

### Ulepszono
- Ustawienie „Powiadomienia o prośbach” nazywa się teraz „Powiadomienia o prośbach i odpowiedziach”, bo obejmuje też gotowe odpowiedzi.

#### PL Tytuł
Wiadomości, które czekają na sieć

#### PL Najważniejsze
Wiadomość wysłana bez internetu czeka w czacie i wychodzi sama, gdy wróci sieć.

#### EN Highlights
A message you write with no network waits in the chat and sends itself when the connection comes back.

#### EN New Features
- Messages without a network are not lost. When you write to an agent offline, the message waits in the chat with “No connection” and sends itself when the network returns.
  - It still works after you close and reopen the app.
  - Several waiting messages send one after another, and a short notice appears once they have gone out.
- You know when a reply is ready, even while the app is in the background.
  - The tab title shows how many new replies there are, for example “(2) Agentic OS”. The count disappears when you come back.
  - With notifications on, the phone shows the start of the reply, or that the task failed.

#### EN Improvements
- The setting “Powiadomienia o prośbach” is now “Powiadomienia o prośbach i odpowiedziach”, because it also covers finished replies.


## v0.8.0 – Slash Commands in the Chat
_02.11.2026 · przenumerowane z v0.14.0_

### Dodano
- Polecenia w czacie: wpisz „/”, a nad polem wiadomości pojawi się lista. Działa dotknięciem albo strzałkami i Enterem.
  - „/zapamiętaj …” – agent zapamięta to na stałe, bez wysyłania wiadomości.
  - „/notatka …” – tekst trafia od razu do Wiedzy.
  - „/codziennie …” – otwiera planowanie, żeby agent robił to sam codziennie.
  - „/nowa” zaczyna nową rozmowę, a „/historia” otwiera poprzednie.
  - Polskie znaki są opcjonalne: „/zapamietaj” też działa.

### Ulepszono
- Niewysłana wiadomość nie znika: gdy wyjdziesz z rozmowy albo z aplikacji, tekst czeka w polu po powrocie, osobno dla każdego agenta.
- Na komputerze strzałka w górę w pustym polu otwiera edycję Twojej ostatniej wiadomości.

#### PL Tytuł
Polecenia ukośnika w czacie

#### PL Najważniejsze
Wpisz „/” w czacie, a nad polem wiadomości pojawi się lista poleceń.

#### EN Highlights
Type “/” in the chat and a list of commands appears above the message field.

#### EN New Features
- Chat commands: type “/” and a list appears above the message field. It works by touch or with the arrow keys and Enter.
  - “/zapamiętaj …” — the agent remembers it for good, without sending a message.
  - “/notatka …” — the text goes straight into Knowledge.
  - “/codziennie …” — opens scheduling so the agent does it every day on its own.
  - “/nowa” starts a new conversation, and “/historia” opens previous ones.
  - Polish diacritics are optional: “/zapamietaj” works too.

#### EN Improvements
- An unsent message stays put: when you leave the conversation or the app, the text is still in the field when you come back, separately for each agent.
- On a computer, the up arrow in an empty field opens your last message for editing.


## v0.7.4 – Welcoming Empty Screens
_02.11.2026 · przenumerowane z v0.13.0_

### Dodano
- Nowa rozmowa z agentem wita Cię zamiast pustego ekranu: agent przedstawia się i proponuje 4 gotowe pytania.
  - Jedno dotknięcie wysyła pytanie, np. „Co potrafisz? Pokaż na przykładach” albo „Zaplanuj mi tydzień”.
  - Agent z krótkim własnym opisem pokazuje go w powitaniu.

### Ulepszono
- Pusta lista zadań mówi, co się na niej pojawi, i ma przyciski „Napisz do agenta” i „Zaplanuj zadanie”.
- Ekran startowy ma delikatną poświatę w kolorze akcentu, a szybkie zadania mają kolorowe ikony.
- Nagłówki „Na dziś” i „Szybkie zadania” nie są już podkreślone jak linki i wyglądają jak reszta nagłówków w aplikacji.

#### PL Tytuł
Przyjazne puste ekrany

#### PL Najważniejsze
Nowa rozmowa wita Cię i proponuje 4 gotowe pytania zamiast pustego ekranu.

#### EN Highlights
A new conversation greets you and offers 4 ready-made questions instead of an empty screen.

#### EN New Features
- A new conversation with an agent greets you instead of an empty screen: the agent introduces itself and suggests 4 ready-made questions.
  - One tap sends a question, for example “Co potrafisz? Pokaż na przykładach” or “Zaplanuj mi tydzień”.
  - An agent with a short description of its own shows that description in the greeting.

#### EN Improvements
- An empty task list says what will appear there, and has buttons “Napisz do agenta” and “Zaplanuj zadanie”.
- The start screen has a soft glow in the accent colour, and quick tasks have coloured icons.
- The headings “Na dziś” and “Szybkie zadania” are no longer underlined like links and look like the other headings in the app.


## v0.7.3 – Smoother Chat and Conversation Search
_02.11.2026 · przenumerowane z v0.12.0_

### Dodano
- Wyszukiwanie w historii rozmów: po tytule i po treści wszystkich wiadomości.
  - Gdy pasuje treść, pod tytułem widać fragment wiadomości z szukanym słowem.
  - Polskie znaki są opcjonalne: „lodz” znajdzie „Łódź”, a „zrob” znajdzie „zrób”.

### Ulepszono
- Czat nie przewija się już sam na dół, gdy czytasz wcześniejsze wiadomości. Zamiast tego pojawia się przycisk „↓ Nowa odpowiedź” (albo „Agent czeka na Twoją decyzję”), który przenosi na dół jednym dotknięciem.
  - Daleko w górze rozmowy przycisk „Na dół” pozwala szybko wrócić do najnowszych wiadomości.
- Nowa odpowiedź agenta pojawia się płynnie, akapit po akapicie. Przy włączonym w telefonie ograniczeniu animacji pojawia się od razu.

#### PL Tytuł
Płynniejszy czat i wyszukiwanie rozmów

#### PL Najważniejsze
Historię rozmów przeszukasz po tytule i po treści, a czat nie ucieka na dół, gdy czytasz starsze wiadomości.

#### EN Highlights
You can search conversation history by title and by message text, and the chat no longer jumps to the bottom while you are reading.

#### EN New Features
- Search in conversation history: by title and by the text of every message.
  - When the message text matches, a snippet with the word you looked for shows under the title.
  - Polish diacritics are optional: “lodz” finds “Łódź”, and “zrob” finds “zrób”.

#### EN Improvements
- The chat no longer scrolls itself to the bottom while you are reading earlier messages. A “↓ Nowa odpowiedź” button appears instead (or “Agent czeka na Twoją decyzję”) and takes you down in one tap.
  - Far up in the conversation, a “Na dół” button takes you back to the newest messages.
- A new reply appears smoothly, paragraph by paragraph. If the phone has animations limited, it appears at once.


## v0.7.2 – Stop and Regenerate Replies
_02.11.2026 · przenumerowane z v0.11.0_

### Dodano
- Przycisk „Zatrzymaj” w czacie, gdy agent pracuje nad odpowiedzią.
  - Agent naprawdę przestaje pracować na serwerze: nie wykonuje kolejnych kroków i nie wysyła już kolejnych zapytań do modelu.
  - Gdy agent czekał na Twoją zgodę, zatrzymanie odpowiada „nie” i kończy zadanie.
  - Zatrzymana odpowiedź ma przycisk „Spróbuj ponownie”, a w zakładce Zadania jest oznaczona jako „zatrzymane”.
- „Wygeneruj ponownie” pod ostatnią odpowiedzią agenta: inna odpowiedź na to samo pytanie bez przepisywania go. Poprzednia odpowiedź znika też z pamięci agenta.

### Naprawiono
- Odpowiedź, która zakończyła się błędem, ma pod spodem przycisk „Spróbuj ponownie”.

### Drobne zmiany
- Skill `/scal-i-sprawdz` dla Claude Code w repozytorium (`.claude/skills/`): scala PR, gdy testy są zielone, a potem po kolei sprawdza opisy wydań i nowe wydanie.

#### PL Tytuł
Zatrzymaj i wygeneruj odpowiedź ponownie

#### PL Najważniejsze
Przycisk „Zatrzymaj” kończy pracę agenta na serwerze, a „Wygeneruj ponownie” prosi o inną odpowiedź na to samo pytanie.

#### EN Highlights
“Zatrzymaj” stops the agent on the server, and “Wygeneruj ponownie” asks for another reply to the same question.

#### EN New Features
- A “Zatrzymaj” button in the chat while the agent is working on a reply.
  - The agent really stops on the server: it does not take further steps and does not send further requests to the model.
  - If the agent was waiting for your approval, stopping answers “no” and ends the task.
  - A stopped reply has a “Spróbuj ponownie” button, and in the Tasks tab it is marked as stopped.
- “Wygeneruj ponownie” under the agent's last reply: another answer to the same question without typing it again. The previous reply is also forgotten by the agent.

#### EN Bug Fixes
- A reply that ended in an error has a “Spróbuj ponownie” button under it.

#### EN Docs & CI
- A `/scal-i-sprawdz` skill for Claude Code in the repository (`.claude/skills/`): it merges a PR when the checks are green, then checks the release notes and the new release one step at a time.


## v0.7.1 – Formatted Replies: Lists, Tables and Code
_01.11.2026 · przenumerowane z v0.10.0_

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

#### PL Tytuł
Sformatowane odpowiedzi: listy, tabele i kod

#### PL Najważniejsze
Odpowiedzi agentów pokazują listy, tabele i kod zamiast surowych znaczków Markdown.

#### EN Highlights
Agent replies show lists, tables and code instead of raw Markdown marks.

#### EN New Features
- Agent replies are formatted, instead of showing raw Markdown marks (#, *, |, ```).
  - Headings, bulleted and numbered lists (including nested ones), quotes and dividers.
  - Tables with a header that scroll sideways on a narrow screen.
  - Code blocks with the language name and a “Kopiuj” button that copies only the code.
  - Clickable links, opened in a new tab (http and https addresses only).
  - Bold, italic and inline code.
  - Formatting is safe: HTML in an agent reply is shown as plain text and never runs.

#### EN Improvements
- Reply previews in “Na dziś” show plain text, without formatting marks.
- Notices (for example “Skopiowano”) appear at the top of the screen while a dialog is open, instead of covering the list in the dialog.


## v0.7.0 – Conversation History
_01.11.2026 · przenumerowane z v0.9.0_

### Dodano
- Historia rozmów w czacie, jak w innych aplikacjach AI: przycisk „Rozmowy” w nagłówku rozmowy.
  - Lista poprzednich rozmów z agentem: tytuł z pierwszego pytania, dzień, godzina i liczba wiadomości.
  - Dotknięcie rozmowy otwiera ją z powrotem. Agent pamięta jej przebieg, dopóki serwer nie został uruchomiony ponownie.
  - Przy każdej rozmowie jest „✕”, żeby usunąć ją z historii.
  - Historia trzyma 20 ostatnich rozmów z każdym agentem, w tej przeglądarce lub aplikacji.

### Zmieniono
- „Nowa rozmowa” nie kasuje już poprzedniej rozmowy, tylko odkłada ją do historii.

#### PL Tytuł
Historia rozmów

#### PL Najważniejsze
W czacie jest historia rozmów: poprzednie rozmowy z agentem można otworzyć albo usunąć.

#### EN Highlights
The chat keeps a history of conversations, and you can reopen or remove them.

#### EN New Features
- Conversation history in the chat, as in other AI apps: a “Rozmowy” button in the conversation header.
  - A list of previous conversations with the agent: a title from the first question, the day, the time and the number of messages.
  - Tapping a conversation opens it again. The agent remembers it until the server is restarted.
  - Each conversation has an “✕” to remove it from the history.
  - The history keeps the last 20 conversations with each agent, in this browser or app.

#### EN Improvements
- “Nowa rozmowa” no longer deletes the previous conversation. It files it in the history.


## v0.6.2 – Reply Actions and One-Tap Follow-Ups
_01.11.2026 · przenumerowane z v0.8.0_

### Dodano
- Akcje pod każdą odpowiedzią agenta w czacie: odpowiedź nie kończy już rozmowy.
  - „Kopiuj”: cała odpowiedź trafia do schowka.
  - „Udostępnij” (na telefonie): wysyłasz odpowiedź dalej, np. przez komunikator albo e-mail.
  - „Rób to codziennie”: jednym dotknięciem pytanie staje się zaplanowanym zadaniem. Formularz otwiera się z nazwą, treścią i agentem już wpisanymi, wystarczy wybrać godzinę i zapisać.
- Szybkie odpowiedzi pod ostatnią odpowiedzią agenta: „Krócej”, „Więcej szczegółów” i „W punktach” wysyłają gotową prośbę bez pisania.

#### PL Tytuł
Akcje pod odpowiedzią i szybkie dopowiedzenia

#### PL Najważniejsze
Pod odpowiedzią agenta możesz ją skopiować, udostępnić, zrobić z niej zadanie codzienne albo poprosić o inną formę.

#### EN Highlights
Under an agent reply you can copy it, share it, turn it into a daily task, or ask for another shape.

#### EN New Features
- Actions under every agent reply in the chat: a reply no longer ends the conversation.
  - “Kopiuj”: the whole reply goes to the clipboard.
  - “Udostępnij” (on the phone): you send the reply on, for example through a messenger or email.
  - “Rób to codziennie”: one tap turns the question into a scheduled task. The form opens with the name, the text and the agent already filled in; you only pick the time and save.
- Quick replies under the agent's last reply: “Krócej”, “Więcej szczegółów” and “W punktach” send a ready-made request without typing.


## v0.6.1 – Connect AI in 60 Seconds
_01.11.2026 · przenumerowane z v0.7.0_

### Dodano
- „Połącz AI w 60 sekund”: prowadzone podłączenie modelu AI zamiast długiego formularza. Otwiera się z przycisku „Połącz AI” na ekranie startowym i w zakładce Modele.
  - Wybór jednym dotknięciem: Google Gemini (darmowy, zalecany), OpenRouter (darmowe modele) albo Anthropic Claude.
  - Krótka instrukcja i link prosto do strony, na której tworzy się dostęp.
  - Pole z przyciskiem „Wklej” i podpowiedzią, gdy wpis wygląda na niepełny.
  - Wpis od razu jest sprawdzany. Po sukcesie: „Gotowe!” i przycisk „Zadaj pierwsze pytanie” z gotowym pytaniem na start.
  - Inni dostawcy (OpenAI, Groq, Ollama…) dalej są w zakładce Modele.

### Naprawiono
- Usunięcie dostawcy ustawionego jako domyślny przywraca model z ustawień serwera. Wcześniej aplikacja dalej pokazywała go jako połączony, choć nie działał.
- Wpis, który nie przeszedł sprawdzenia w „Połącz AI”, nie zostaje zapisany jako działający dostawca.

#### PL Tytuł
Połącz AI w 60 sekund

#### PL Najważniejsze
„Połącz AI w 60 sekund” prowadzi przez podłączenie modelu zamiast długiego formularza.

#### EN Highlights
“Połącz AI w 60 sekund” walks you through connecting a model instead of a long form.

#### EN New Features
- “Połącz AI w 60 sekund”: a guided way to connect an AI model instead of a long form. It opens from the “Połącz AI” button on the start screen and in the Models tab.
  - One tap to choose: Google Gemini (free, recommended), OpenRouter (free models) or Anthropic Claude.
  - A short instruction and a link straight to the page where you create access.
  - A field with a “Wklej” button and a hint when the text looks incomplete.
  - The text is checked at once. On success: “Gotowe!” and a “Zadaj pierwsze pytanie” button with a ready-made first question.
  - Other providers (OpenAI, Groq, Ollama…) are still in the Models tab.

#### EN Bug Fixes
- Removing the provider that was set as the default restores the model from the server settings. Previously the app still showed it as connected even though it did not work.
- Text that failed the check in “Połącz AI” is not saved as a working provider.


## v0.6.0 – Today Feed on the Start Screen
_01.11.2026_

### Dodano
- Sekcja „Na dziś” na ekranie startowym: od razu widać, co wymaga uwagi i co agenci zrobili, gdy Cię nie było.
  - Decyzje, na które czekają agenci, są na samej górze i prowadzą prosto do rozmowy z agentem.
  - Wyniki zaplanowanych zadań z ostatniej doby („Poranne podsumowanie – gotowe”) z fragmentem odpowiedzi. Znikają z listy, gdy je otworzysz.
  - „Kontynuuj rozmowę” z ostatnim agentem i fragmentem jego ostatniej odpowiedzi.
  - Najbliższe zaplanowane zadanie, np. „jutro o 07:30”.
  - Gdy nie masz jeszcze zaplanowanych zadań: propozycja „Niech agent pracuje, gdy śpisz”, która otwiera gotowy do zapisania formularz porannego podsumowania.
  - Sekcja nie wysyła nic do modelu AI, więc nic nie kosztuje.

### Ulepszono
- Pole „Napisz do agenta…” na ekranie startowym jest zawsze widoczne nad dolnym menu, także gdy ekran trzeba przewinąć.

#### PL Tytuł
Sekcja „Na dziś” na ekranie startowym

#### PL Najważniejsze
Sekcja „Na dziś” pokazuje, co wymaga uwagi i co agenci zrobili, gdy Cię nie było.

#### EN Highlights
The “Na dziś” section shows what needs you and what agents did while you were away.

#### EN New Features
- A “Na dziś” section on the start screen: you immediately see what needs attention and what agents did while you were away.
  - Decisions the agents are waiting on sit at the top and open straight into the conversation.
  - Results of scheduled tasks from the last day (“Poranne podsumowanie – gotowe”) with a snippet of the reply. They leave the list when you open them.
  - “Kontynuuj rozmowę” with the last agent and a snippet of its last reply.
  - The next scheduled task, for example “jutro o 07:30”.
  - When you have no scheduled tasks yet: a suggestion “Niech agent pracuje, gdy śpisz”, which opens a morning-summary form ready to save.
  - The section sends nothing to the AI model, so it costs nothing.

#### EN Improvements
- The “Napisz do agenta…” field on the start screen stays visible above the bottom menu, even when the screen has to scroll.


## v0.5.0 – Message Editing, Agent Screen and Usage Counter
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
- Licznik zużycia w zakładce Modele: ile pracy poszło na wejściu i wyjściu oraz ile było zapytań, bez kwot.
  - Przełącznik okresu: Dziś, 7 dni, Miesiąc.
  - Suma z podziałem na wejście i wyjście oraz wykres dzień po dniu.
  - Lista dostawców z liczbą zapytań i zużycia każdego z nich.
  - Liczenie zaczyna się od tej wersji: wcześniejsze dni pokazują 0.

### Naprawiono
- Aplikacja na Androida: aparat, mikrofon i zmiana adresu serwera działają na nowych telefonach.
  - „Skanuj kod QR z komputera” włącza aparat na żywo i sam odczytuje kod. Aplikacja pyta o dostęp do aparatu przy pierwszym użyciu. Przycisk „Zrób zdjęcie” zostaje jako zapas.
  - Przycisk mikrofonu otwiera systemowe rozpoznawanie mowy telefonu, a rozpoznany tekst trafia do pola wiadomości. Aplikacja nie potrzebuje do tego dostępu do mikrofonu.
  - Adres serwera zmienisz w zakładce Ty → Adres serwera. Działa też przy nawigacji gestami, gdzie nie da się przytrzymać przycisku Wstecz.

### Ulepszono
- Formularz zaplanowanego zadania pokazuje, kiedy zadanie uruchomi się pierwszy raz, np. „Następne uruchomienie: jutro o 07:30”.
- Gdy zmieniasz adres dostawcy z zapisanym dostępem, pole od razu prosi o wpisanie go ponownie (zapisany dostęp nie jest wysyłany pod nowy adres).

#### PL Tytuł
Edycja wiadomości, ekran agenta i licznik zużycia

#### PL Najważniejsze
Możesz poprawić wysłaną wiadomość, włączać skille na ekranie agenta i zobaczyć zużycie modelu bez kwot.

#### EN Highlights
You can edit a sent message, toggle skills on the agent screen, and see model usage without prices.

#### EN New Features
- Editing a sent message in the chat, as in other AI apps.
  - Under each of your messages there is an “Edytuj” pencil: you correct the text and send it again.
  - Replies after that message disappear from the screen and from the agent's memory, so the agent answers as if the previous version had not existed.
  - Editing waits until the agent finishes answering. Esc or “Anuluj” leaves the message unchanged.
- An agent screen: in You → Agents each agent has an “✏️ Edytuj” button.
  - At the top, the agent's icon, its name and the model it uses.
  - The “Skille” card shows every available skill as a tile: a tap turns a skill on or off (an enabled one is green, with a check).
  - Every tap saves at once, with no “Zapisz” button. For 5 seconds a “Włączono: …” notice appears at the bottom with an “Cofnij” button.
  - A long press on a tile (or the right mouse button) shows the skill's description, its tools and its instructions, with an on/off button.
  - The agent's permissions, thinking mode, conversations and approvals stay as they are.
- A usage counter in the Models tab: how much went in and out, and how many requests there were, without prices.
  - A period switch: Today, 7 days, Month.
  - A total split into input and output, and a day-by-day chart.
  - A list of providers with each one's requests and usage.
  - Counting starts with this version: earlier days show 0.

#### EN Bug Fixes
- The Android app: the camera, the microphone and changing the server address work on newer phones.
  - “Skanuj kod QR z komputera” turns the camera on live and reads the code itself. The app asks for camera access the first time. “Zrób zdjęcie” stays as a fallback.
  - The microphone button opens the phone's speech recognition, and the recognized text goes into the message field. The app does not need microphone access for that.
  - You change the server address in You → Server address. It also works with gesture navigation, where you cannot hold the Back button.

#### EN Improvements
- The scheduled-task form shows when the task will run the first time, for example “Następne uruchomienie: jutro o 07:30”.
- When you change a provider address that already has access saved, the field asks you to type it again at once (the saved access is not sent to the new address).


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
- Logowanie do War Room działa też wtedy, gdy wklejony tekst ma spację albo nową linię na końcu.
- Obraz Dockera ma obsługę PDF i gotowy folder na dane, więc zapisywanie działa od razu po podpięciu wolumenu.

### Ulepszono
- Więcej zadań może naraz czekać na Twoją zgodę lub odpowiedź, nie blokując czatu.
- Serwer działający długo nie zajmuje coraz więcej pamięci: pamięta ostatnie 500 zakończonych zadań.
- Bezpieczeństwo:
  - po wielu próbach błędnego logowania trzeba odczekać kilka minut;
  - serwery MCP uruchamiane na serwerze nie dostają jego danych logowania;
  - zbyt duże albo podejrzane pliki i obliczenia są odrzucane, zamiast obciążać serwer;
  - automatyczne wdrożenie na Oracle nie zapisuje danych logowania do GitHuba w plikach repozytorium.
- Dokumentacja: aktualna lista funkcji serwera w README i poprawna komenda Dockera z trwałymi danymi.

#### PL Tytuł
Niezawodniejszy zapis, planowanie, harmonogram i modele

#### PL Najważniejsze
Zapis ustawień nie zostawia już uszkodzonego pliku, a harmonogram i modele są odporniejsze na błędy.

#### EN Highlights
Saving settings no longer leaves a damaged file, and schedules and models cope better with errors.

#### EN Bug Fixes
- Settings, agents, skills, mods, the schedule and memory save safely: a crash in the middle of a save no longer leaves a damaged file.
  - If a file is damaged anyway, the server sets it aside and starts normally, instead of failing to start.
  - A broken line in the knowledge base is skipped, and the rest of the documents stay.
- Removing a model provider no longer deletes the agents that used it: they move to the default model.
- Planning goals and the work of a team of agents no longer ends in an error when the model returns an unusual plan.
- OpenAI-compatible models with a lower reply limit (for example DeepSeek) and newer OpenAI models work: the app adjusts the limit itself after the first refusal.
- Switching models during a conversation (for example from Claude to Gemini) no longer breaks that conversation.
- The schedule:
  - changing the time, or turning a task back on after its time has passed, does not run it immediately, only the next day;
  - “wyłączone” sent as text really turns the task off;
  - one error (for example a full disk) no longer stops the schedule for good.
- Logging in to the War Room still works when the pasted text has a space or a new line at the end.
- The Docker image can read PDFs and has a ready folder for data, so saving works as soon as you attach a volume.

#### EN Improvements
- More tasks can wait at once for your approval or your answer, without blocking the chat.
- A server that runs for a long time does not keep using more memory: it remembers the last 500 finished tasks.
- Safety:
  - after many failed login attempts you have to wait a few minutes;
  - MCP servers started on this server do not receive its login data;
  - files or calculations that are too large or look wrong are rejected, instead of loading the server;
  - automatic deployment to Oracle does not save GitHub login data in repository files.
- Documentation: an up-to-date list of server features in the README and a correct Docker command with durable data.


## v0.4.1 – Security and Stability Fixes from the Audit
_31.10.2026_

### Naprawiono
- Lepsza ochrona serwera uruchomionego na własnym komputerze bez logowania: przyjmuje tylko prośby z tego samego komputera i odrzuca te wysłane przez inne strony internetowe.
- Zapisane dane logowania do modeli nie trafią tam, gdzie nie powinny:
  - po zmianie adresu dostawcy modelu albo moda trzeba wpisać je ponownie, zamiast wysyłać zapisane pod nowy adres;
  - połączenie nie idzie za przekierowaniem na inny serwer;
  - edycja dostawcy bez wpisywania danych logowania nie zastępuje zapisanych danych ich zamaskowaną wersją („••••”).
- Kilku agentów może naraz zapisywać wspomnienia: wcześniej odpowiedź potrafiła przepaść z błędem, a plik pamięci mógł się uszkodzić. Pamięć zapisuje się teraz w całości albo wcale.
- Wgrywanie dokumentów do bazy wiedzy nie przerywa już agentów, którzy w tym czasie z niej korzystają.
- Nowe komunikaty o tych zabezpieczeniach są wyjaśnione po polsku w War Room.

#### PL Tytuł
Poprawki bezpieczeństwa i stabilności po audycie

#### PL Najważniejsze
Serwer na własnym komputerze i zapisane dane logowania do modeli są lepiej chronione.

#### EN Highlights
A server on your own computer, and saved model login data, are better protected.

#### EN Bug Fixes
- Better protection for a server started on your own computer without a login: it accepts only requests from that same computer and rejects ones sent by other websites.
- Saved model login data does not go where it should not:
  - after you change a model provider's address, or a mod's, you have to type it again, instead of sending the saved data to the new address;
  - a connection does not follow a redirect to another server;
  - editing a provider without typing the login data does not replace the saved data with its masked form (“••••”).
- Several agents can save memories at the same time: previously a reply could be lost with an error, and the memory file could be damaged. Memory now saves completely or not at all.
- Uploading documents to the knowledge base no longer interrupts agents that are using it at the same time.
- New messages about these protections are explained in Polish in the War Room.


## v0.4.0 – "Server Asleep" Screen Instead of a 404
_31.10.2026_

### Dodano
- Ekran „Serwer śpi” zamiast pustej strony z błędem 404, gdy serwer War Room nie odpowiada (np. Codespace zasnął po 30 minutach bez używania).
  - Wyjaśnia po ludzku, co się stało, i zapewnia, że agenci i dane są bezpieczne.
  - Prowadzi w 3 krokach: przycisk otwierający Codespaces, gotowe komendy do włączenia serwera z przyciskiem „Kopiuj komendy” i tekstem wpisywanym tak, żeby nie było go widać.
  - Sam sprawdza serwer co 5 sekund i od razu wraca do War Room, gdy ten wstanie. Nic nie trzeba odświeżać.
  - Działa w przeglądarce i w aplikacji na Androida, także bez internetu, w jasnym i ciemnym motywie.

#### PL Tytuł
Ekran „Serwer śpi” zamiast błędu 404

#### PL Najważniejsze
Gdy serwer War Room nie odpowiada, zamiast pustej strony 404 widać ekran „Serwer śpi”.

#### EN Highlights
When the War Room server does not answer, a “Serwer śpi” screen appears instead of an empty 404 page.

#### EN New Features
- A “Serwer śpi” screen instead of an empty 404 page when the War Room server does not answer (for example a Codespace fell asleep after 30 minutes without use).
  - It explains in plain language what happened, and that the agents and the data are safe.
  - It leads you in 3 steps: a button that opens Codespaces, ready commands to start the server with a “Kopiuj komendy” button, and text you type so it stays hidden.
  - It checks the server every 5 seconds and returns to the War Room as soon as it is up. Nothing has to be refreshed.
  - It works in the browser and in the Android app, also with no network, in light and dark themes.


## v0.3.1 – New Android App Key
_19.10.2026_

> Instalacja: Przed instalacją tej wersji raz odinstaluj poprzednią aplikację. Kolejne wersje będą się już instalować na tej.
> Install: Uninstall the previous app once before installing this version. Later versions install over this one.

### Zmieniono
- Aplikacja na Androida korzysta z nowego klucza, którego nie ma w repozytorium. Dzięki temu nikt poza tym projektem nie może wydać wersji, którą telefon uzna za aktualizację.
  - Przed instalacją tej wersji trzeba raz odinstalować poprzednią, bo Android nie pozwala podmienić aplikacji przy tej zmianie.
  - Po instalacji podaj ponownie adres serwera i dane logowania do War Room. Dla pewności warto przy okazji je zmienić.

### Drobne zmiany
- Opisy wydań są rozszerzone: gdy zmiana obejmuje kilka elementów (np. agentów i ich skille), każdy jest wypisany jako podpunkt.

#### PL Tytuł
Nowy klucz aplikacji na Androida

#### PL Najważniejsze
Aplikacja na Androida korzysta z nowego klucza spoza repozytorium. Tę wersję trzeba raz zainstalować od nowa.

#### EN Highlights
The Android app uses a new key that is not in the repository. Install this version once from scratch.

#### EN Improvements
- The Android app uses a new key that is not in the repository. Nobody outside this project can publish a build the phone will treat as an update.
  - Before installing this version, uninstall the previous app once, because Android will not replace the app across this change.
  - After installing, enter the server address and the War Room login again. This is a good moment to change that login.

#### EN Docs & CI
- Release notes are more detailed: when a change covers several parts (for example agents and their skills), each one is listed as a sub-point.


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

#### PL Tytuł
Gotowy zespół 5 agentów i 25 skilli

#### PL Najważniejsze
Jednym przyciskiem dodasz 5 gotowych agentów, każdy z 5 skillami ze swojej działki.

#### EN Highlights
One button adds 5 ready-made agents, each with 5 skills from its own field.

#### EN New Features
- A ready-made team: 5 agents, each with 5 skills from its own field. You add them with one button in You → Agents → 📦 Gotowy zespół. They use the default model.
  - 🏪 **Mała firma** (`mala-firma`): cash flow (Cash Flow Snapshot), a sales campaign (Run Campaign), tax preparation (Tax Prep), a pay plan (Plan Payroll), chasing overdue invoices (Invoice Chase).
  - 📱 **Social media** (`social-media`): posts for LinkedIn and others (Post Writer), learning your writing style (Voice Builder), strong opening lines (Hook Generator), scripts for reels and shorts (Reels Scripting), profile improvements (Profile Optimizer).
  - 💻 **Programista** (`programista`): orderly work on code: plan, tests, debugging, review (Superpowers), project memory (Memory Keeper), creating new skills (Skill Creator), building MCP servers (MCP Builder), current library documentation, including through Context7 (Docs Fetcher).
  - 🎨 **Projektant** (`projektant`): a full UI/UX system (UI UX Pro Max), a brand book (Brand Guidelines), page prototypes in one HTML file (Web Artifacts), front-end code (Frontend Design), design critique with a score and fixes (Taste).
  - 📣 **Marketing** (`marketing`): sales copy (Copywriting), materials in exchange for joining a list (Lead Magnets), analysis of customer opinions (Customer Research), raising conversion (CRO), visibility in AI search and Google (AI SEO).
- The skills are written in Polish especially for Agentic OS. Agents do not quote tax rates or deadlines from memory, and they do not invent numbers or opinions.


## v0.2.8 – Clear Notice When No AI Model Is Set
_18.10.2026_

### Ulepszono
- Gdy agent nie ma ustawionego modelu AI, jego odpowiedź zaczyna się od jasnej uwagi po polsku, że to tryb testowy bez AI, i mówi, gdzie ustawić model. Wcześniej pokazywał niezrozumiały tekst po angielsku.

#### PL Tytuł
Jasny komunikat, gdy nie ustawiono modelu AI

#### PL Najważniejsze
Gdy agent nie ma modelu AI, odpowiedź zaczyna się od jasnej uwagi po polsku, gdzie go ustawić.

#### EN Highlights
When an agent has no AI model, the reply starts with a clear Polish notice that says where to set one.

#### EN Improvements
- When an agent has no AI model set, its reply starts with a clear Polish notice that this is a test mode without AI, and says where to set a model. Previously it showed confusing English text.


## v0.2.7 – Clear OpenRouter Privacy Errors
_18.10.2026_

### Ulepszono
- War Room wyjaśnia po polsku dwa częste błędy OpenRoutera i podaje, co zmienić:
  - brak dostawcy modelu zgodnego z Twoimi ustawieniami prywatności (np. ZDR), z linkiem do tych ustawień;
  - model, który nie obsługuje narzędzi używanych przez agenta.

### Drobne zmiany
- Zmiana samej instrukcji aplikacji na Androida nie tworzy już nowego wydania.
- Ponowne zbudowanie tej samej wersji dostaje dopisek po plusie, np. v0.2.6+build.1, a wydanie może mieć w opisie własną uwagę.

#### PL Tytuł
Zrozumiałe błędy prywatności OpenRoutera

#### PL Najważniejsze
War Room wyjaśnia po polsku dwa częste błędy OpenRoutera i podaje, co zmienić.

#### EN Highlights
The War Room explains two common OpenRouter errors in Polish and says what to change.

#### EN Improvements
- The War Room explains two common OpenRouter errors in Polish and says what to change:
  - no model provider matches your privacy settings (for example ZDR), with a link to those settings;
  - a model that does not support the tools the agent uses.

#### EN Docs & CI
- A change that only touches the Android app's instructions no longer creates a new release.
- Building the same version again gets a suffix after a plus, for example v0.2.6+build.1, and a release can carry its own note.


## v0.2.6 – Versioned APK File Names & Test Builds
_15.10.2026_

> Uwaga: To wydanie powstało automatycznie po zmianach w automatyzacji wydań i w instrukcji instalacji. Aplikacja jest taka sama jak w v0.2.5, zmienił się tylko numer wersji pokazywany w ustawieniach Androida i nazwa pliku. Nie musisz jej aktualizować.
> Note: This release was created automatically after changes to release automation and the install instructions. The app is the same as in v0.2.5; only the version number shown in Android settings and the file name changed. You do not have to update.

### Zmieniono
- Plik aplikacji w każdym wydaniu ma w nazwie numer wersji, np. AgenticOS_v0.2.6.apk. W starszych wydaniach zmieniła się tylko nazwa pliku, sam plik jest ten sam.
- Można wydawać wersje testowe alpha, beta i rc (np. v0.3.0-beta.1) oznaczone jako „Pre-release”.
- Wydania sprzed zmiany numeracji mają w opisie uwagę, że ich aplikacja pokazuje dawny numer wersji zapisany w pliku APK.

#### PL Tytuł
Nazwy plików APK z numerem wersji i wydania testowe

#### PL Najważniejsze
Plik aplikacji ma w nazwie numer wersji. Sam program jest taki sam jak w v0.2.5.

#### EN Highlights
The app file name includes the version number. The app itself is the same as in v0.2.5.

#### EN Docs & CI
- The app file in every release has the version number in its name, for example AgenticOS_v0.2.6.apk. In older releases only the file name changed; the file itself is the same.
- Test builds can be published as alpha, beta and rc (for example v0.3.0-beta.1), marked as “Pre-release”.
- Releases from before the numbering change say in their notes that the app shows the old version number stored in the APK file.


## v0.2.5 – Semantic Versioning & Readable Release Titles
_15.10.2026_

### Zmieniono
- Wydania mają numery wersji w formacie v0.X.Y i krótkie angielskie tytuły, np. „v0.2.1 – Clear Connection Errors in the Android App”. Wcześniejsze wydania dostały nowe numery i nazwy według tej samej zasady.

#### PL Tytuł
Numeracja SemVer i czytelne tytuły wydań

#### PL Najważniejsze
Wydania mają numery v0.X.Y i krótkie angielskie tytuły.

#### EN Highlights
Releases use v0.X.Y numbers and short English titles.

#### EN Docs & CI
- Releases have version numbers in the form v0.X.Y and short English titles, for example “v0.2.1 – Clear Connection Errors in the Android App”. Earlier releases received new numbers and names on the same principle.


## v0.2.4 – Bilingual Release Names
_15.10.2026 · dawniej android-16_

### Zmieniono
- Nazwy wydań na GitHubie są teraz po polsku i angielsku, np. „Agentic OS – wydanie 14 · Release 14”.

#### PL Tytuł
Dwujęzyczne nazwy wydań

#### PL Najważniejsze
Nazwy wydań na GitHubie są po polsku i po angielsku.

#### EN Highlights
Release names on GitHub are in Polish and in English.

#### EN Docs & CI
- Release names on GitHub are now in Polish and in English, for example “Agentic OS – wydanie 14 · Release 14”.


## v0.2.3 – A Release for Every Important Change
_15.10.2026 · dawniej android-14_

### Zmieniono
- Nowe wydanie powstaje po każdej ważnej zmianie w Agentic OS, a nie tylko po zmianach w aplikacji na Androida. Drobiazgi trafiają do opisu najbliższego wydania zamiast tworzyć osobne.

#### PL Tytuł
Wydanie przy każdej ważnej zmianie

#### PL Najważniejsze
Nowe wydanie powstaje po każdej ważnej zmianie, a drobiazgi czekają na najbliższy opis.

#### EN Highlights
A new release is published after every important change, and small items wait for the next notes.

#### EN Docs & CI
- A new release is created after every important change in Agentic OS, not only after changes to the Android app. Small items go into the notes of the next release instead of creating one of their own.


## v0.2.2 – Release Notes in Polish
_15.10.2026 · dawniej android-11_

### Dodano
- Każde wydanie na GitHubie ma teraz opis po polsku: co dodano, co zmieniono, co usunięto, jakie błędy naprawiono i co ulepszono.

#### PL Tytuł
Opisy wydań po polsku

#### PL Najważniejsze
Każde wydanie na GitHubie ma opis po polsku: co dodano, co zmieniono i co naprawiono.

#### EN Highlights
Every GitHub release has Polish notes: what was added, changed, removed, fixed and improved.

#### EN New Features
- Every GitHub release now has a description in Polish: what was added, what changed, what was removed, which bugs were fixed and what was improved.


## v0.2.1 – Clear Connection Errors in the Android App
_15.10.2026 · dawniej android-9_

### Ulepszono
- Aplikacja na Androida nie pokazuje już technicznych kodów błędów. Gdy coś nie działa, widać krótkie wyjaśnienie po polsku, np. brak internetu, serwer wyłączony albo zły adres.
- Ekran błędu ma przyciski „Spróbuj ponownie” i „Zmień adres serwera” oraz pasuje do jasnego i ciemnego motywu telefonu.
- Okno adresu serwera samo poprawia częste literówki i mówi wprost, co jest nie tak z wpisanym adresem.

### Naprawiono
- Aplikacja rozpoznaje, gdy serwer w chmurze jest uśpiony lub wyłączony, i mówi o tym zamiast pokazywać pustą stronę.
- Adres zapisany w starszej wersji, który nie może działać, nie blokuje już aplikacji: przy starcie pojawia się prośba o poprawny.

#### PL Tytuł
Zrozumiałe błędy połączenia w aplikacji na Androida

#### PL Najważniejsze
Aplikacja na Androida pokazuje krótkie wyjaśnienie po polsku zamiast technicznych kodów błędów.

#### EN Highlights
The Android app shows a short Polish explanation instead of technical error codes.

#### EN Improvements
- The Android app no longer shows technical error codes. When something does not work, you see a short Polish explanation, for example no network, the server is off, or a wrong address.
- The error screen has “Spróbuj ponownie” and “Zmień adres serwera” buttons and fits light and dark phone themes.
- The server-address dialog corrects common typos itself and says plainly what is wrong with the address you typed.

#### EN Bug Fixes
- The app recognizes when the server in the cloud is asleep or off, and says so instead of showing an empty page.
- An address saved by an older version, which cannot work, no longer blocks the app: at startup it asks for a valid one.


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
- Modele: licznik dzisiejszych zapytań z opcjonalnym dziennym limitem, lista modeli prosto od dostawcy i informacja, czy dostęp działa.
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

#### PL Tytuł
Nowy War Room, zadania cykliczne i pliki wiedzy

#### PL Najważniejsze
War Room ma nowy wygląd, zadania cykliczne i wgrywanie plików do wiedzy.

#### EN Highlights
The War Room has a new look, recurring tasks, and file upload into Knowledge.

#### EN New Features
- A new War Room look (version C) with light, dark and system themes and four accent colours.
- A bottom bar with five tabs: Chat, Tasks, Knowledge, Models and You.
- A chat start screen with agent cards and “Szybkie zadania”, and voice typing in browsers that support it.
- The agent's requests for approval, and its questions, appear in the conversation, with the time left to answer.
- Recurring tasks: an agent can do a task on its own every day, on weekdays or at weekends, at a chosen time.
- A progress bar for tasks in progress and a preview of finished replies.
- Knowledge: uploading PDF, DOCX, TXT and MD files, searching inside documents and deleting them.
- Models: a counter of today's requests with an optional daily limit, a list of models straight from the provider, and whether access works.
- Notifications of the agent's requests when the app is in the background (in browsers that support it).
- Logging the phone in with a QR code shown on the computer.
- Choosing a model from a list instead of typing the name by hand.
- A warning in the chat when no AI model is set.

#### EN Improvements
- Less used sections (Agents, Extensions, Monitoring) moved to the You tab, and Brain and memory import moved to the Knowledge tab.
- Every error that can appear is explained in plain Polish, with a hint of what to do next. The full error text is available under “Szczegóły”.
- When a model provider is briefly overloaded, the app tries again on its own before it shows an error.

#### EN Bug Fixes
- An agent's reply is no longer lost when the connection drops, the page reloads or the tab is closed: the conversation comes back, and the reply appears when it is ready.
- A wrong “Failed to fetch” message in the chat when the reply was already ready in Tasks.
- Unreadable text made of the word “null” repeated in the task details.


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

#### PL Tytuł
Pierwsze wydanie Agentic OS i aplikacji na Androida

#### PL Najważniejsze
Pierwsze wydanie: War Room w aplikacji na Androida, która łączy się z Twoim serwerem.

#### EN Highlights
The first release: the War Room in an Android app that connects to your server.

#### EN New Features
- The first release of the Agentic OS Android app: the War Room in an app that connects to your server.
- Agentic OS: AI agents with tools, memory, a knowledge base, planning and learning from ratings.
- The War Room: a browser app for talking to agents, managing them and watching their work, which can also be installed on a phone.
- Support for Gemini, Claude and OpenAI-compatible providers, and also external agents, MCP servers, skills and your own tools.
- Agent permissions: from “always ask” to full independence, changeable at any time.
- Importing memory from other AI assistants.
- Instructions for running on a free cloud server, and a file of instructions for AI assistants that build and update the project.

#### EN Improvements
- Gemini also works without the extra Google library, so installation is simpler.

#### EN Bug Fixes
- A rare problem with saving settings when several things saved at the same time.

