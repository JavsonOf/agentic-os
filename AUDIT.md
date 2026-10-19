# Pełny Raport z Audytu i Analizy Projektu Agentic OS (War Room + Core + Android)

## Spis treści
1. [Podsumowanie architektury projektu](#1-podsumowanie-architektury-projektu)
2. [Błędy krytyczne i bezpieczeństwo (do pilnej naprawy)](#2-błędy-krytyczne-i-bezpieczeństwo-do-pilnej-naprawy)
3. [Błędy w kodzie, współbieżności, pamięci i stabilności (do naprawy)](#3-błędy-w-kodzie-współbieżności-pamięci-i-stabilności-do-naprawy)
4. [Przypadki brzegowe dostawców LLM (Claude, Gemini, OpenAI-compat)](#4-przypadki-brzegowe-dostawców-llm-claude-gemini-openai-compat)
5. [Błędy zapisu stanu i trwałości danych (Persistence)](#5-błędy-zapisu-stanu-i-trwałości-danych-persistence)
6. [Co można ulepszyć w kodzie i architekturze](#6-co-można-ulepszyć-w-kodzie-i-architekturze)
7. [Co warto dodać, aby używanie aplikacji było swobodne i bezproblemowe (UX)](#7-co-warto-dodać-aby-używanie-aplikacji-było-swobodne-i-bezproblemowe-ux)

---

## 1. Podsumowanie architektury projektu

- **Backend (Python 3.10+)**: Modułowy system operacyjny dla agentów AI bez zewnętrznych zależności w rdzeniu (`agentic_os/`). Zawiera własny serwer HTTP oparty o `ThreadingHTTPServer` (`agentic_os/server/__init__.py`), pulę wątków dla procesów agentów (`kernel.py`), bazę wektorową + BM25 (RAG), pamięć krótko- i długoterminową, obsługę MCP (stdio/HTTP), modów HTTP, skilli oraz harmonogramów zadań.
- **Frontend (War Room PWA)**: Jednostronicowa aplikacja mobilna w czystym JS/CSS (`agentic_os/server/static/index.html`, `app.js`, `app.css`, `errors.js`, `qr.js`, `sw.js`) z polskim interfejsem i tłumaczeniem błędów technicznych na przystępny język.
- **Aplikacja Android (`android/`)**: Lekki klient WebView w Javie (`MainActivity`, `Friendly`) budowany automatycznie przez GitHub Actions do pliku APK.
- **Wdrożenie (`Dockerfile`, `deploy/`)**: Obraz Dockerowy oraz automatyczny skrypt cloud-init dla Oracle Cloud Always Free z HTTPS przez Caddy i auto-aktualizacją.

---

## 2. Błędy krytyczne i bezpieczeństwo (do pilnej naprawy)

### 2.1. Service Worker (`sw.js`) cache'uje prywatne odpowiedzi API i psuje wylogowanie
- **Plik**: `agentic_os/server/static/sw.js` (linie 13–22)
- **Opis problemu**: Service Worker przechwytuje **każde** żądanie `GET` w obrębie tej samej domeny (nie tylko pliki statyczne z listy `ASSETS`) i zapisuje jego odpowiedź w `CacheStorage` (`agentic-os-v6`).
- **Skutek**:
  1. Wrażliwe dane zwracane przez `/providers`, `/agents`, `/processes`, `/approvals`, `/knowledge`, `/graph` zostają zapisane w pamięci podręcznej przeglądarki i nie są czyszczone przy wylogowaniu.
  2. Gdy serwer jest wyłączony lub niedostępny, `fetch().catch(() => caches.match(e.request))` zwraca przestarzałe odpowiedzi JSON z cache'u (np. dla `/auth/check` lub `/processes`), przez co aplikacja maskuje brak połączenia i pokazuje stare dane.
- **Rozwiązanie**: W `sw.js` obsługiwać z cache'u wyłącznie ścieżki znajdujące się na liście statycznych zasobów `ASSETS`.

### 2.2. Brak uprawnień kamery (QR) i mikrofonu w aplikacji Android (WebView)
- **Pliki**: `android/app/src/main/AndroidManifest.xml` (linie 1–10), `android/app/src/main/java/os/agentic/warroom/MainActivity.java` (linie 93–111), `agentic_os/server/static/app.js` (linie 90–110, 374–386)
- **Opis problemu**: Ekran logowania posiada przycisk „Skanuj kod QR z komputera” (`navigator.mediaDevices.getUserMedia`), a ekran czatu ma przycisk mikrofonu (`webkitSpeechRecognition`). Jednak aplikacja Android:
  1. Deklaruje w `AndroidManifest.xml` wyłącznie `INTERNET` oraz `ACCESS_NETWORK_STATE` (brak `CAMERA` i `RECORD_AUDIO`).
  2. W `MainActivity.java` klasa `WebChromeClient` nie implementuje metody `onPermissionRequest(PermissionRequest request)`.
- **Skutek**: Skanowanie kodu QR oraz wprowadzanie głosowe nie działają w aplikacji Android APK.
- **Rozwiązanie**: Dodać uprawnienia w `AndroidManifest.xml`, obsługę runtime permissions w `MainActivity.java` oraz `onPermissionRequest` w `WebChromeClient`.

### 2.3. Brak możliwości zmiany adresu serwera na Androidzie 13–15 (nawigacja gestami)
- **Plik**: `android/app/src/main/java/os/agentic/warroom/MainActivity.java` (linie 187–215)
- **Opis problemu**: Otwarcie okna zmiany adresu serwera po pierwszym połączeniu wymaga długiego przytrzymania przycisku Wstecz (`onKeyLongPress(KEYCODE_BACK)`). Na nowoczesnych smartfonach z nawigacją gestami (przesunięcie od krawędzi) system Android nie generuje długiego naciśnięcia `KEYCODE_BACK`.
- **Skutek**: Użytkownik nie może zmienić adresu serwera bez czyszczenia danych aplikacji w ustawieniach systemu lub wywołania błędu sieci.
- **Rozwiązanie**: Dodać w zakładce „Ty” (`#panel-me`) przycisk „Zmień adres serwera” widoczny w aplikacji Android (`isApp()`), który kieruje pod obsługiwany już adres `agentic-os://settings`.

### 2.4. Brak paczki `pdf` (`pypdf`) w `Dockerfile`
- **Pliki**: `Dockerfile` (linia 6), `pyproject.toml` (linia 18)
- **Opis problemu**: `Dockerfile` wykonuje `pip install --no-cache-dir ".[anthropic,gemini]"`, pomijając opcjonalny dodatek `pdf` (`pypdf>=4`).
- **Skutek**: Na serwerze uruchomionym przez Docker (w tym na Oracle Cloud) wgrywanie plików PDF do bazy wiedzy (`/knowledge/upload`) nie korzysta z biblioteki `pypdf`, lecz z awaryjnego parsera strumieni zlib, który nie odczytuje tekstu z większości współczesnych dokumentów PDF.
- **Rozwiązanie**: Zmienić instalację w `Dockerfile` na `".[anthropic,gemini,pdf]"`.

### 2.5. Podatność CSRF prowadząca do RCE na lokalnym serwerze (`127.0.0.1`)
- **Pliki**: `agentic_os/server/__init__.py` (linie 130–149, 268–272), `agentic_os/mcp.py` (linie 114–118)
- **Opis problemu**:
  1. Przy domyślnym uruchomieniu lokalnym (`127.0.0.1:8000`) zmienna `AGENTIC_OS_API_KEY` nie jest wymagana.
  2. Metoda `Handler._body()` czyta i parsuje JSON bez sprawdzania, czy nagłówek `Content-Type` to `application/json`.
  3. W przeglądarkach żądanie `POST` z `Content-Type: text/plain` jest tzw. „simple request” i jest wysyłane bez zapytania kontrolnego CORS `OPTIONS`.
  4. Endpoint `POST /mcp` przyjmuje `{"name":"x","transport":"stdio","command":"..."}` i natychmiast uruchamia podaną komendę przez `subprocess.Popen`.
- **Skutek**: Dowolna strona internetowa otwarta w przeglądarce na tym samym komputerze może po cichu wysłać żądanie `fetch("http://127.0.0.1:8000/mcp", ...)` i wykonać dowolny kod na komputerze użytkownika.
- **Rozwiązanie**: W `_body()` wymagać nagłówka `Content-Type: application/json` oraz blokować żądania zawierające nagłówek `Origin` z obcej domeny.

### 2.6. Ujemny `Content-Length` omija limity wielkości żądania (`MAX_BODY` i `MAX_UPLOAD`)
- **Plik**: `agentic_os/server/__init__.py` (linie 131–136, 232–235, 246–249)
- **Opis problemu**: Kod sprawdza `if length > MAX_BODY:` oraz `if not length:`, a następnie wywołuje `self.rfile.read(length)`. Gdy klient wyśle nagłówek `Content-Length: -1`, oba warunki są fałszywe, a `self.rfile.read(-1)` w Pythonie czyta dane bez limitu aż do EOF.
- **Rozwiązanie**: Sprawdzać `if length < 0 or length > MAX_BODY:`.

### 2.7. Białe znaki w `AGENTIC_OS_API_KEY` całkowicie blokują logowanie
- **Plik**: `agentic_os/server/__init__.py` (linie 142–149), `agentic_os/config.py` (linia 45)
- **Opis problemu**: Serwer robi `.strip()` na tokenie przychodzącym w nagłówku `Authorization`, ale nie robi `.strip()` na zmiennej środowiskowej `AGENTIC_OS_API_KEY`. Jeśli hasło w zmiennej środowiskowej lub pliku `.env` ma na końcu spację lub znak nowej linii, `hmac.compare_digest` zawsze zwraca `False` i nie da się zalogować.
- **Rozwiązanie**: Dodać `.strip()` przy odczycie `AGENTIC_OS_API_KEY` w `config.py`.

### 2.8. Ryzyko SSRF (Server-Side Request Forgery) i bomb dekompresyjnych (ZIP/XML/PDF)
- **Pliki**: `agentic_os/mods.py` (linia 42), `agentic_os/rag/extract.py` (linie 45–50, 99), `agentic_os/memory/importer.py` (linie 169–177), `agentic_os/tools/builtin.py` (linia 42), `agentic_os/llm/mock.py` (linia 44)
- **Opis problemów**:
  1. Mody HTTP są automatycznie oznaczane tagiem `"readonly"` dla metody `GET`, przez co agenci w trybie `"smart"` mogą bez pytania odpytywać wewnętrzne adresy sieciowe serwera (np. `169.254.169.254` lub `127.0.0.1`).
  2. Ekstraktor DOCX używa `xml.etree.ElementTree.fromstring` bez blokady encji XML (podatność Billion Laughs) i bez limitu rozmiaru po rozpakowaniu, a ekstraktor PDF wywołuje `zlib.decompress(data)` bez parametru `max_length`.
  3. W kalkulatorze (`safe_eval` w `builtin.py:42`) sprawdzany jest tylko prawy operand potęgowania (`abs(right) > 1000`). Wyrażenie `((9**1000)**1000)**1000` ma w każdym węźle wykładnik 1000, ale generuje liczbę o miliardzie cyfr i zawiesza proces Pythona.
  4. W `llm/mock.py:44` wyrażenie regularne `_MATH` ma cztery nakładające się kwantyfikatory `[-+*/().\d\s^%]*`, co powoduje katastrofalny backtracking ($O(N^3)$) na długich ciągach cyfr i spacji.

---

## 3. Błędy w kodzie, współbieżności, pamięci i stabilności (do naprawy)

### 3.1. Wyciek pętli `pollApprovals()` po wylogowaniu i duplikacja timerów
- **Plik**: `agentic_os/server/static/app.js` (linie 223–232, 577–580, 673)
- **Opis problemu**: Funkcja `pollApprovals()` w bloku `finally` bezwarunkowo planuje kolejne wywołanie `approvalTimer = setTimeout(pollApprovals, 3000)`. Po kliknięciu „Wyloguj” (`#logout-btn`) timer nie jest zatrzymywany: co 3 sekundy wysyła zapytanie `/approvals`, otrzymuje HTTP 401 i wywołuje `showLogin()`, które czyści komunikat błędu `#login-error` na ekranie logowania. Ponadto ponowne zalogowanie wywołuje `start()`, które uruchamia kolejną równoległą pętlę `pollApprovals()`.
- **Rozwiązanie**: Wywoływać `clearTimeout(approvalTimer)` wewnątrz `showLogin()` oraz przed startem pętli w `start()`.

### 3.2. Zagłodzenie puli wątków (`ThreadPoolExecutor`) przez oczekujące zgody (`Approval`)
- **Plik**: `agentic_os/kernel.py` (linie 206, 369–384, 540–556)
- **Opis problemu**: `self._executor` ma domyślnie tylko `max_workers=4`. Każde zadanie w tle lub czat (`async=True`), w którym agent czeka na zatwierdzenie narzędzia przez operatora lub odpowiedź na pytanie (`ask_user`), blokuje wątek roboczy na `item._event.wait(300.0)` (do 5 minut). Wystarczą 4 oczekujące pytania/zgody, aby całkowicie zablokować możliwość pisania na czacie i wykonywania jakichkolwiek zadań w całym systemie.
- **Rozwiązanie**: Zwiększyć pulę wątków roboczych (np. do 16–32) lub wydzielić osobną pulę dla zadań oczekujących.

### 3.3. Brak synchronizacji (`threading.Lock`) w `VectorStore`, `BM25Index`, `RAGPipeline` i `LongTermMemory`
- **Pliki**: `agentic_os/memory/vector_store.py` (linie 29–77), `agentic_os/rag/bm25.py` (linie 10–48), `agentic_os/memory/long_term.py` (linie 23–50)
- **Opis problemu**: Żadna z tych klas nie posiada blokady wątkowej. Gdy jeden wątek (np. kończący pracę agent zapisujący epizod w `agents/base.py:190` lub import pamięci/wiedzy) dodaje lub usuwa rekordy, a drugi wątek iteruje po słowniku `self._records.values()` lub `self._docs.items()` (podczas wyszukiwania RAG, budowania grafu `/graph` lub zapisu `memory.json`), Python rzuca wyjątek `RuntimeError: dictionary changed size during iteration`.
- **Rozwiązanie**: Dodać `threading.RLock()` w `VectorStore` i `BM25Index` lub iterować po kopiach (`list(self._records.values())`).

### 3.4. Wyścig wątków na buforze rozmowy (`ConversationBuffer`) oraz `ToolRegistry`
- **Pliki**: `agentic_os/kernel.py` (linie 225–226, 259–272, 546–556), `agentic_os/memory/short_term.py` (linie 16–47), `agentic_os/tools/registry.py` (linie 166–203)
- **Opis problemu**:
  1. Wątek w tle `_reconnect_mcp` uruchamiany przy starcie modyfikuje słownik `self.mcp` oraz `self.tools` bez blokady `self._lock`.
  2. Równoległe wiadomości wysłane w tej samej sesji czatu współdzielą ten sam obiekt `ConversationBuffer` bez synchronizacji odczytu/zapisu tur.

### 3.5. Śmierć wątku harmonogramu (`scheduler`) i błąd przycisku „Uruchom teraz”
- **Pliki**: `agentic_os/kernel.py` (linie 647–671), `agentic_os/schedules.py` (linie 92–93, 130–131)
- **Opis problemu**:
  1. Metoda `ScheduleStore.due()` iteruje po `self._items.values()` bez blokady `self._lock`. Jeśli w tym samym ułamku sekundy użytkownik doda lub usunie harmonogram w UI, wyjątek `RuntimeError` poza blokiem `try` w `run_due_schedules()` zabije wątek `agentic-os-scheduler` na stałe aż do restartu serwera.
  2. Kliknięcie „Uruchom teraz” (`POST /schedules/{id}/run`) wywołuje `run_schedule()`, które od razu zapisuje `last_run = dzisiejsza_data`. Jeśli użytkownik przetestuje zadanie ręcznie przed godziną zaplanowaną w harmonogramie, zadanie nie wykona się już automatycznie tego dnia.
- **Rozwiązanie**: Dodać `with self._lock:` w `ScheduleStore.all()` i `due()`, opakować pętlę `loop()` w `start_scheduler` w `try...except`, a w `run_schedule()` aktualizować `last_run` tylko dla uruchomień automatycznych (lub przekazywać flagę `manual=True`).

### 3.6. Tryb refleksyjny (`_ReflectiveRunner`) zapisuje nieudane próby do pamięci długoterminowej
- **Pliki**: `agentic_os/kernel.py` (linie 157–184), `agentic_os/agents/base.py` (linie 189–192)
- **Opis problemu**: `_ReflectiveRunner` podmienia `worker.memory` na `_ReadOnlyMemory`, aby odrzucone próby nie zaśmiecały historii czatu, ale zostawia aktywne `worker.long_term`. Przez to każda nisko oceniona próba (nawet z wynikiem 0.1) jest zapisywana jako `episode` w `LongTermMemory` i pobierana jako kontekst przy kolejnych próbach. Dodatkowo licznik tokenów w `_ReflectiveRunner` nie uwzględnia tokenów zużytych przez sędziego (`LLMJudge`) i krytykę (`_critique`).
- **Rozwiązanie**: Na czas prób w `_ReflectiveRunner` ustawić `worker.remember_episodes = False`, a epizod zapisać w `LongTermMemory` tylko raz — dla najlepszej wybranej próby.

### 3.7. Nieograniczony wzrost pamięci RAM (`self.processes`, `self._rewards`, `self._sessions`)
- **Plik**: `agentic_os/kernel.py` (linie 203, 208, 214, 503–507, 565–571)
- **Opis problemu**: Wszystkie utworzone procesy (wraz z pełnymi wynikami i historią kroków) są przechowywane w `self.processes` bez żadnego limitu. Każde wywołanie `GET /processes` sortuje całą historię od początku działania serwera.
- **Rozwiązanie**: Dodać rotację/limit zakończonych procesów w pamięci (np. ostatnie 500 zadań).

### 3.8. Błędy w CLI (`--provider gemini`), koercji `Optional` w narzędziach i procesach MCP
- `agentic_os/cli.py` (linia 86): `choices=["auto", "anthropic", "mock"]` nie pozwala przekazać `--provider gemini`, mimo że reszta systemu obsługuje Gemini.
- `agentic_os/tools/registry.py` (linie 46–51, 137–154): Funkcja `_coerce()` przy przekazanym `None` dla opcjonalnego parametru `str | None` zwraca ciąg znaków `"None"`, a dla `int | None` lub `bool | None` rzuca `ToolError`. Jeśli wartość wynosi `None`, a parametr nie jest w `required`, `_coerce` powinno zwracać `None`.
- `agentic_os/mcp.py` (linie 161–163): `_StdioTransport.close()` wywołuje `self.proc.terminate()`, ale nie wywołuje `self.proc.wait(timeout=2)` ani nie zamyka potoków `stdin`/`stdout`, zostawiając procesy-zombie (`<defunct>`).

---

## 4. Przypadki brzegowe dostawców LLM (Claude, Gemini, OpenAI-compat)

### 4.1. Crash przy przełączeniu modelu (np. z Claude na Gemini) w trakcie rozmowy
- **Pliki**: `agentic_os/kernel.py` (linie 330–338), `agentic_os/llm/anthropic_provider.py` (linie 98–100), `agentic_os/llm/gemini_provider.py` (linie 97–99)
- **Opis problemu**: `Message.raw` przechowuje surową odpowiedź specyficzną dla danego SDK (`list` bloków w Anthropic, obiekt `Content` z `.parts` w Gemini). Gdy użytkownik zmieni domyślny model i napisze kolejną wiadomość w tej samej sesji czatu:
  - `to_gemini_contents()` wykonuje `msg.raw.parts` na liście z Anthropica i rzuca `AttributeError: 'list' object has no attribute 'parts'`.
  - `to_anthropic_messages()` przekazuje `list(msg.raw)` z obiektu Gemini do API Anthropica, co kończy się błędem walidacji 400.
- **Rozwiązanie**: Sprawdzać zgodność typu `msg.raw` w `to_gemini_contents()` oraz `to_anthropic_messages()`, a gdy pochodzi od innego dostawcy — odtwarzać wiadomość z uniwersalnych pól `msg.content` i `msg.tool_calls`.

### 4.2. Niezłapane wyjątki SDK w `AnthropicProvider` i `GeminiProvider`
- **Pliki**: `agentic_os/llm/anthropic_provider.py` (linie 68–72), `agentic_os/llm/gemini_provider.py` (linie 72–76)
- **Opis problemu**: W przeciwieństwie do `OpenAICompatProvider`, natywne providery Anthropic i Gemini nie opakowują wyjątków SDK (`anthropic.APIError`, `google.genai.errors.APIError`) w klasę `LLMError`. Przez to serwer HTTP zwraca status 500 zamiast 400, a destylacja pamięci w `import_memory` przerywa działanie zamiast pominąć błędny rekord.

### 4.3. Niedopasowane `max_tokens=16000` w `OpenAICompatProvider`
- **Plik**: `agentic_os/llm/openai_compat.py` (linie 134–138)
- **Opis problemu**: Każde wywołanie wysyła sztywne `"max_tokens": 16000`. Wiele modeli na OpenRouterze, Groq, Mistral czy starsze modele OpenAI ma maksymalny limit wyjścia 4096 lub 8192 tokenów i odrzuca żądanie błędem 400. Z kolei nowe modele rozumujące OpenAI (`o1`, `o3`, `o4-mini`) wymagają parametru `max_completion_tokens`.

### 4.4. Niekompatybilne parametry beta w `AnthropicProvider`
- **Plik**: `agentic_os/llm/anthropic_provider.py` (linie 65–72)
- **Opis problemu**: Przy domyślnym `fallbacks=True` wywoływane jest `self.client.beta.messages.create(**params, betas=["server-side-fallback-2026-07-01"], fallbacks="default")`, oraz zawsze dodawane jest `output_config={"effort": self.effort}`. Standardowe wersje biblioteki `anthropic` oraz starsze modele Claude (np. Haiku/Sonnet 3.5) mogą odrzucać argument `fallbacks` (`TypeError`) lub `output_config`.

### 4.5. Urwana tura z wynikami narzędzi po przekroczeniu `max_steps`
- **Plik**: `agentic_os/agents/base.py` (linie 142–189)
- **Opis problemu**: Jeśli w ostatnim kroku (`max_steps`) model zażąda wywołania narzędzia, pętla wykonuje narzędzie, dopisuje `Message.tool(...)` na koniec tury i kończy działanie z `stopped_reason = "max_steps"`, zapisując turę zakończoną rolą `"tool"` do `ConversationBuffer`. Przy kolejnej wiadomości użytkownika po wiadomości `"tool"` następuje bezpośrednio wiadomość `"user"`, co powoduje błąd 400 w restrykcyjnych API zgodnych z OpenAI.

---

## 5. Błędy zapisu stanu i trwałości danych (Persistence)

### 5.1. Nieatomowy zapis plików JSON grożący uszkodzeniem danych przy restarcie
- **Pliki**: `agentic_os/providers.py` (linie 118–123), `agentic_os/mods.py` (linie 109–114), `agentic_os/skills.py` (linie 72–75), `agentic_os/memory/vector_store.py` (linie 66–71)
- **Opis problemu**: Metody `_save()` w tych czterech modułach otwierają plik docelowy bezpośrednio w trybie zapisu z obcięciem (`O_TRUNC` / `"w"`) zamiast zapisać dane do pliku tymczasowego `.tmp` i podmienić go przez `os.replace()`. Jeśli w trakcie zapisu nastąpi utrata zasilania, zabicie kontenera lub wyścig wątków (szczególnie w `memory.json`, które jest zapisywane po każdym zadaniu agenta!), plik zostaje uszkodzony, a przy kolejnym starcie `AgenticOS` nie uruchomi się z powodu `json.JSONDecodeError`.

### 5.2. Nadpisanie prawdziwego klucza API zamaskowanym ciągiem `••••••••`
- **Pliki**: `agentic_os/providers.py` (linie 133–136), `agentic_os/server/__init__.py` (linie 268–301), `agentic_os/server/static/app.js` (linie 526–544)
- **Opis problemu**:
  1. `ProviderRegistry.upsert()` zachowuje dotychczasowy klucz tylko wtedy, gdy `not config.api_key`. Jeśli klient prześle z powrotem zamaskowany klucz z `GET /providers` (`"••••••••1234"`), prawdziwy klucz zostanie zastąpiony kropkami. W `POST /mcp` i `POST /agents/external` w ogóle nie ma zachowywania dotychczasowego klucza przy aktualizacji.
  2. W `app.js:534` funkcja `fillProviderForm(p, isPreset = false)` ustawia `E.make_default.checked = isPreset && !state.providers.length;`, przez co edycja aktualnie domyślnego dostawcy odznacza checkbox „Ustaw jako domyślny”.

---

## 6. Co można ulepszyć w kodzie i architekturze

### 6.1. Synchronizacja historii czatu z serwerem (zamiast tylko `localStorage`)
- Obecnie dymki czatu są zapisywane tylko w `localStorage` przeglądarki (`aos_chats` w `app.js:113`), a serwer trzyma swój `ConversationBuffer` tylko w pamięci RAM.
- **Skutek**: Historia rozmów nie synchronizuje się między telefonem a komputerem, a po restarcie serwera w aplikacji widać starą rozmowę, której serwer już nie pamięta.
- **Ulepszenie**: Utrwalać sesje czatu na serwerze (w `AGENTIC_OS_DATA_DIR`) i udostępnić endpoint `GET /chat?agent=...&session=...`.

### 6.2. Odporność na uszkodzone pliki JSON przy starcie systemu
- W `_load_json()` w `kernel.py` oraz w konstruktorach rejestrów (`providers`, `mods`, `skills`, `schedules`, `vector_store`) warto dodać obsługę `(OSError, ValueError)` z zapisem kopii uszkodzonego pliku `.corrupt`, aby pojedynczy uszkodzony plik nigdy nie blokował startu całego serwera.

### 6.3. Optymalizacja fizyki grafu w zakładce „Mózg” (`app.js:400-433`)
- Symulacja odpychania węzłów ma złożoność $O(N^2)$ w 300 iteracjach podczas jednego wywołania przed rysowaniem. Przy większej liczbie dokumentów i wspomnień warto rozłożyć symulację na klatki `requestAnimationFrame` lub ograniczyć zasięg odpychania.

---

## 7. Co warto dodać, aby używanie aplikacji było swobodne i bezproblemowe (UX)

### 7.1. Strumieniowanie odpowiedzi na żywo (Streaming / SSE) + podgląd używanych narzędzi
- **Problem**: Podczas długich zadań użytkownik widzi jedynie „Myślę… (krok 2/10)” i czeka na całą odpowiedź naraz, nie wiedząc, jakie narzędzie jest w tej chwili wywoływane.
- **Co dodać**: Strumieniowanie tokenów w czasie rzeczywistym (lub zwracanie w statusie procesu nazwy aktualnie wykonywanego narzędzia i częściowej odpowiedzi).

### 7.2. Przycisk „Zatrzymaj” (Anulowanie trwającego zadania / czatu)
- **Problem**: Jeśli agent zapętli się w narzędziach lub użytkownik zauważy błąd w swoim pytaniu, nie ma sposobu na przerwanie działania procesu.
- **Co dodać**: Przycisk „Zatrzymaj” w oknie rozmowy i na liście zadań (`POST /processes/{pid}/cancel`), który ustawia flagę przerwania sprawdzaną między krokami pętli agenta.

### 7.3. Renderowanie Markdown w czacie + przycisk „Kopiuj”
- **Problem**: W `app.js:254-261` wiadomości są wyświetlane przez zwykłe `textContent`. Kod źródłowy, tabele, listy punktowane i pogrubienia wyświetlają surowe znaczniki (`**`, ```` ``` ````, `|`), a skopiowanie bloku kodu na telefonie jest bardzo niewygodne.
- **Co dodać**: Lekki, bezpieczny parser Markdown (escape HTML + formatowanie bloków kodu, list, pogrubień, linków) oraz przycisk „Kopiuj” przy każdym bloku kodu i pod odpowiedzią agenta.

### 7.4. Załączanie plików bezpośrednio w oknie czatu (ikona spinacza)
- **Problem**: Aby przeanalizować plik PDF, CSV lub TXT w rozmowie, trzeba wyjść z czatu, przejść do zakładki „Wiedza”, wgrać plik, wrócić do czatu i dopiero zadać pytanie.
- **Co dodać**: Przycisk załącznika obok pola wpisywania wiadomości w czacie, który automatycznie wgrywa plik i przekazuje jego treść/kontekst bezpośrednio do bieżącej rozmowy.

### 7.5. Wiele wątków rozmów (sesji) z tym samym agentem
- **Problem**: W UI każdy agent ma tylko jedną sesję (`"default"`). Rozpoczęcie nowego tematu wymaga skasowania poprzedniej rozmowy („Nowa rozmowa”).
- **Co dodać**: Listę/przełącznik wątków rozmów dla każdego agenta (backend w `kernel.py:546` obsługuje już parametr `session`).

### 7.6. Globalny pasek oczekujących zatwierdzeń (`Approvals`) i powiadomienia
- **Problem**: Pasek `#approvals-bar` z pytaniem od agenta lub prośbą o zgodę na narzędzie wyświetla się **tylko** wewnątrz widoku aktywnej rozmowy (`#view-convo`). Gdy użytkownik przełączy się na inną zakładkę, nie widzi, że agent czeka na jego decyzję, aż po 5 minutach mija timeout.
- **Co dodać**: Umieścić `#approvals-bar` na poziomie globalnego kontenera `#app` (widoczny w każdej zakładce) oraz dodać odznakę (badge) na pasku nawigacji i opcjonalne powiadomienia systemowe (`Notification API`).

### 7.7. Eksport i import pełnej kopii zapasowej (Backup / Restore ZIP) w zakładce „Ty”
- **Problem**: Przeniesienie skonfigurowanych agentów, skilli, modów, harmonogramów, pamięci i bazy wiedzy na inny serwer lub telefon wymaga ręcznego kopiowania plików z katalogu `AGENTIC_OS_DATA_DIR` przez SSH.
- **Co dodać**: Przyciski „Pobierz kopię zapasową (.zip)” oraz „Przywróć z kopii” bezpośrednio w zakładce „Ty” w War Roomie.
