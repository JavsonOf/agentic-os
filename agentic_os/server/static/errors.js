"use strict";
/* Agentic OS War Room: every error the server, the model providers or MCP servers can report,
   explained in plain Polish with what to do next. The raw text stays available as "Szczegóły".
   Each rule is [pattern, message]; a message can be a function of the regex match and the full text.
   Rules are checked in order, so specific ones come before general ones. */

function _waitText(text) {
  const m = text.match(/retry in (?:(\d+)h)?(?:(\d+)m)?(\d+(?:\.\d+)?)s/i) || text.match(/"retryDelay":\s*"(\d+)s"/);
  if (!m) return "";
  const secs = m.length === 2 ? Number(m[1]) : Number(m[1] || 0) * 3600 + Number(m[2] || 0) * 60 + Number(m[3]);
  if (secs < 90) return " Spróbuj ponownie za minutę.";
  const h = Math.floor(secs / 3600); const min = Math.round((secs % 3600) / 60);
  return ` Limit odnowi się za ok. ${h ? h + " h " : ""}${min ? min + " min" : ""}`.trimEnd() + ".";
}

const ERROR_RULES = [
  /* ------------------------------------------------ connection between the app and the server */
  [/(?:^|: )Brak połączenia z serwerem/, "📶 Brak połączenia z serwerem Agentic OS. Sprawdź internet i czy serwer (np. Codespaces) nadal działa."],
  [/Failed to fetch|NetworkError|Load failed/i, "📶 Brak połączenia z serwerem Agentic OS. Sprawdź internet i czy serwer (np. Codespaces) nadal działa."],
  [/Missing or invalid API key|Wymagane logowanie/, "🔒 Nieprawidłowe hasło do War Room albo sesja wygasła. Zaloguj się ponownie."],
  [/Przekroczono czas oczekiwania/, "⏱️ Agent pracuje dłużej niż zwykle. Wynik pojawi się w zakładce Zadania, gdy będzie gotowy."],
  [/(?:^|: )No route (?:or item )?for /, "🧩 Ta funkcja nie istnieje na serwerze. Serwer ma starszą wersję niż aplikacja – zrób na serwerze git pull i uruchom go ponownie."],
  [/Request body too large|Plik jest za duży/, "📦 Plik albo tekst jest za duży (limit ok. 60 MB). Podziel go na mniejsze części."],
  [/Forbidden host: without AGENTIC_OS_API_KEY/, "🔒 Serwer bez hasła przyjmuje połączenia tylko z tego samego komputera (localhost). Żeby wejść z innego adresu, uruchom go z hasłem (AGENTIC_OS_API_KEY)."],
  [/Cross-site request refused/, "🔒 Serwer odrzucił prośbę z innej strony internetowej. To ochrona przed atakiem – otwórz War Room bezpośrednio z adresu serwera."],
  [/Re-enter the API key when changing the provider address/, "🔑 Zmieniasz adres dostawcy, więc wpisz klucz API jeszcze raz. Zapisany klucz nie zostanie wysłany pod nowy adres, żeby nie wyciekł."],
  [/Re-enter the mod's headers when changing its address/, "🔑 Zmieniasz adres moda, więc wpisz jego nagłówki (np. klucz API) jeszcze raz. Zapisane wartości nie zostaną wysłane pod nowy adres."],
  [/Refused a redirect to another host \(([^)]+)\)/, (m) => `🔑 Usługa przekierowała połączenie na inny serwer (${m[1]}). Zablokowano to, żeby Twój klucz API tam nie trafił. Sprawdź adres w ustawieniach.`],
  [/(?:^|: )Invalid JSON|JSON body must be an object/, "🧩 Aplikacja wysłała niepoprawne dane. Odśwież stronę i spróbuj ponownie."],

  /* --------------------------------------------------------- external agents (A2A, webhooks) */
  [/A2A error/, "🔌 Zewnętrzny agent (A2A) zgłosił błąd. Sprawdź, czy działa i czy adres jest poprawny."],
  [/from webhook|Cannot reach webhook/, "🔌 Nie udało się połączyć z zewnętrznym agentem (webhook). Sprawdź jego adres i czy działa."],
  [/The openai protocol needs a model id/, "🔌 Dla agenta zgodnego z OpenAI podaj nazwę modelu."],
  [/External agents have no permission or mode settings/, "🔌 Zewnętrzni agenci nie mają ustawień uprawnień ani trybu – te ustawienia dotyczą tylko agentów Agentic OS."],

  /* -------------------------------------------------------------------- MCP servers */
  [/Cannot reach MCP server/, "🧩 Nie można połączyć się z serwerem MCP. Sprawdź jego adres i czy jest uruchomiony."],
  [/HTTP (\d{3}) from MCP server/, (m) => `🧩 Serwer MCP odpowiedział błędem ${m[1]}${m[1] === "401" || m[1] === "403" ? " – brakuje lub jest zły token dostępu" : ""}. Sprawdź jego ustawienia w Ty → Rozszerzenia.`],
  [/MCP server did not answer in time/, "🧩 Serwer MCP nie odpowiedział na czas. Spróbuj ponownie albo uruchom go ponownie."],
  [/MCP process exited|MCP process is not running|MCP server is not connected/, "🧩 Serwer MCP nie działa. Usuń go i dodaj ponownie w Ty → Rozszerzenia albo sprawdź jego polecenie."],
  [/Cannot start MCP command/, "🧩 Nie da się uruchomić polecenia serwera MCP. Sprawdź, czy program jest zainstalowany na serwerze i czy polecenie jest poprawne."],
  [/MCP server sent no response/, "🧩 Serwer MCP nie zwrócił odpowiedzi. Sprawdź, czy to na pewno serwer MCP."],
  [/MCP error/, "🧩 Serwer MCP zgłosił błąd podczas działania narzędzia."],
  [/No MCP server/, "🧩 Ten serwer MCP nie istnieje (mógł zostać usunięty). Odśwież zakładkę Ty → Rozszerzenia."],
  [/A stdio MCP server needs a command/, "🧩 Podaj polecenie, które uruchamia serwer MCP (np. npx …)."],
  [/transport must be/, "🧩 Wybierz sposób połączenia z serwerem MCP: http albo stdio."],

  /* ---------------------------------------------------------- agents, tasks, approvals */
  [/No agent named '([^']+)'/, (m) => `🤖 Agent „${m[1]}” nie istnieje (mógł zostać usunięty). Odśwież stronę i wybierz innego agenta.`],
  [/The default 'assistant' agent cannot be removed/, "🤖 Domyślnego agenta „assistant” nie można usunąć – możesz za to zmienić jego ustawienia."],
  [/No process /, "📋 To zadanie już nie istnieje – serwer został uruchomiony ponownie i wyczyścił listę zadań. Wyślij polecenie jeszcze raz."],
  [/No pending approval/, "⏱️ Ta prośba o zgodę już wygasła (agent czeka 5 minut) albo została obsłużona. Poproś agenta ponownie."],
  [/created in code with a custom strategy/, "🤖 Ten agent został zdefiniowany w kodzie i jego ustawień nie można zmienić z War Room."],
  [/'agents' must be a non-empty list|A crew needs at least one agent/, "👥 Zaznacz co najmniej jednego agenta do zespołu."],
  [/process must be one of/, "👥 Wybierz sposób pracy zespołu z listy."],
  [/mode must be one of/, "🎯 Wybierz tryb agenta z listy (standardowy, refleksyjny albo adaptacyjny)."],
  [/permission must be one of/, "🔐 Wybierz poziom uprawnień z listy."],
  [/'reward' must be a number|reward must be in/, "👍 Ocena musi być liczbą od -1 do 1."],
  [/'answer' must be text|Send 'approve'/, "✋ Odpowiedz agentowi tekstem albo kliknij Zezwól / Odmów."],
  [/Plan has a dependency cycle|depends on unknown task|Duplicate task ids|Plan contains no tasks|No JSON object found in model output|Invalid JSON plan|Plan JSON must be an object/,
    "🗺️ Model nie ułożył poprawnego planu działania. Spróbuj ponownie albo użyj mocniejszego modelu."],
  [/Missing prompt variable/, "📝 W szablonie promptu brakuje wartości dla zmiennych. Uzupełnij je i spróbuj ponownie."],
  [/analysis failed/, "📊 Analiza nie powiodła się. Spróbuj ponownie albo z innym modelem."],
  [/Classifier is not trained/, "📈 Ta funkcja uczenia nie ma jeszcze danych. Oceń kilka odpowiedzi 👍/👎 i spróbuj ponownie."],

  /* ------------------------------------------------------------- AI model providers */
  [/google-genai.*required|'anthropic' package is required/, "📦 Na serwerze brakuje biblioteki dla tego modelu. W terminalu serwera uruchom: pip install -e \".[gemini]\" (albo \".[anthropic]\") i uruchom serwer ponownie."],
  [/A model id is required/, "🤖 Nie podano nazwy modelu. W Modele, w sekcji „Wybierz model”, zaznacz model z listy."],
  [/No provider named|No provider '|Unknown provider/, "🔑 Ten dostawca modeli nie jest skonfigurowany (mógł zostać usunięty). Dodaj go ponownie w Modele albo wybierz innego."],
  [/endpoints? .{0,60}available matching your (?:guardrail|data policy)|No endpoints found matching your data policy|zdr-violation/i, (m, t) => {
    const link = (t.match(/(?:configurable at|Configure:|configure_url"?:\s*"?)\s*(https:\/\/openrouter\.ai\/[^\s"\\,)]+)/i) || [])[1];
    return "🛡️ OpenRouter nie ma dla tego modelu żadnego dostawcy, który spełnia Twoje ustawienia prywatności (np. ZDR – brak zapisywania danych). "
      + `Wybierz w Modele inny model albo zmień te ustawienia: ${(link || "https://openrouter.ai/settings/privacy").replace(/[.]$/, "")}`;
  }],
  [/No endpoints found that support tool use/i, "🧰 Ten model w OpenRouter nie obsługuje narzędzi, z których korzysta agent. Wybierz w Modele inny model, który obsługuje narzędzia (tools)."],
  [/context.{0,20}(length|window)|too many tokens|maximum context|prompt is too long|input.{0,20}too long|exceeds the maximum/i,
    "📏 Rozmowa jest za długa dla tego modelu. Kliknij „Nowa rozmowa” albo wybierz model z większym kontekstem."],
  [/credit balance is too low|insufficient[_ ](quota|funds|balance)|\b402\b|billing/i,
    "💳 Na koncie dostawcy brakuje środków albo płatność nie jest skonfigurowana. Sprawdź rozliczenia u dostawcy (np. Google AI Studio → API keys → Set up billing)."],
  [/RESOURCE_EXHAUSTED|quota|rate[_ ]?limit|Too Many Requests|\b429\b/i, (m, t) => /free_tier|per day|PerDay/i.test(t) || /retry in \d+h/i.test(t)
    ? `⏳ Wykorzystałeś dzienny limit darmowego planu dla tego modelu.${_waitText(t)} Możesz w Modele wybrać inny model albo włączyć płatny plan u dostawcy.`
    : `⏳ Za dużo zapytań w krótkim czasie – dostawca chwilowo blokuje kolejne.${_waitText(t) || " Odczekaj chwilę i spróbuj ponownie."}`],
  [/model.{0,40}(not found|does not exist|no longer available|not supported|is not found)|model_not_found|NOT_FOUND|not_found_error|\b404\b.{0,80}(googleapis|openai|anthropic|models)/i,
    "🔍 Ten model nie istnieje, został wycofany albo nie jest dostępny dla Twojego klucza. W Modele, w sekcji „Wybierz model”, zaznacz inny model z listy."],
  [/API[_ ]?key.{0,30}(invalid|not valid|expired)|API_KEY_INVALID|invalid[_ ]api[_ ]key|incorrect api key|authentication_error|UNAUTHENTICATED|\b401\b/i,
    "🔑 Klucz API jest nieprawidłowy albo wygasł. Wklej poprawny klucz w Modele → Edytuj klucz i limit."],
  [/PERMISSION_DENIED|permission_error|\b403\b/i, "🔑 Klucz API nie ma dostępu do tego modelu lub usługi. Sprawdź uprawnienia klucza u dostawcy albo wybierz inny model."],
  [/high demand|overloaded|UNAVAILABLE|\b503\b|\b529\b/i, "🔥 Serwery tego modelu są teraz przeciążone (to po stronie dostawcy, nie Twojej). Spróbuj za chwilę albo wybierz inny model."],
  [/SAFETY|content[_ ]filter|blocked by|PROHIBITED_CONTENT|"refusal"|stop_reason.{0,5}refusal/i, "🛡️ Dostawca zablokował odpowiedź przez swoje filtry bezpieczeństwa. Spróbuj sformułować prośbę inaczej."],
  [/Cannot reach (https?:\/\/(?!localhost)[^:\s]+)/, (m) => `📶 Serwer Agentic OS nie może połączyć się z ${m[1].replace(/^https?:\/\//, "").split("/")[0]}. Sprawdź internet serwera albo adres dostawcy w Modele.`],
  [/Non-JSON reply from/, "🧩 Dostawca odpowiedział w nieoczekiwany sposób. Sprawdź adres API (base_url) w Modele → Edytuj klucz i limit."],
  [/HTTP 5\d\d from|\b50[0-24]\b.{0,40}(Internal|Bad Gateway|Gateway Timeout|INTERNAL)/i, "🔥 Dostawca modelu ma awarię po swojej stronie. Spróbuj ponownie za chwilę."],
  [/HTTP 400 from|INVALID_ARGUMENT|invalid_request_error/, "🧩 Dostawca odrzucił zapytanie jako niepoprawne (np. ten model nie obsługuje narzędzi). Spróbuj innego modelu z listy."],
  [/timed out|timeout|DEADLINE_EXCEEDED/i, "⏱️ Model nie odpowiedział w wyznaczonym czasie. Spróbuj ponownie albo wybierz szybszy model."],
  [/(?:^|: )Provider error:/, "🤖 Dostawca modelu zgłosił błąd. Spróbuj ponownie albo wybierz inny model."],
  [/ScriptedLLM ran out/, "🧪 Testowy model skończył przygotowane odpowiedzi. Dodaj prawdziwy model w Modele."],

  /* ------------------------------------------------------- knowledge files and schedules */
  [/Unsupported file type: \.(\w*)/, (m) => `📄 Nie umiem odczytać plików .${m[1] || "?"}. Dodaj PDF, DOCX, TXT, MD, CSV albo JSON.`],
  [/DOCX file is damaged/, "📄 Ten plik DOCX jest uszkodzony albo to nie jest dokument Worda. Zapisz go ponownie i spróbuj jeszcze raz."],
  [/No readable text in this PDF/, "📄 W tym PDF nie ma tekstu do odczytania (to pewnie skan albo zdjęcia). Dodaj wersję tekstową albo wklej treść."],
  [/This PDF cannot be read/, "📄 Tego pliku PDF nie da się odczytać (może jest uszkodzony albo zabezpieczony hasłem)."],
  [/A schedule needs a 'task'/, "🗓️ Wpisz, co agent ma zrobić."],
  [/'time' must look like HH:MM/, "🗓️ Podaj godzinę w formacie GG:MM, np. 07:30."],
  [/'days' must be one of/, "🗓️ Wybierz, kiedy zadanie ma się powtarzać."],
  [/No team /, "📦 Tego gotowego zespołu nie ma na serwerze. Odśwież stronę albo zaktualizuj serwer (git pull)."],
  [/No schedule /, "🗓️ To zaplanowane zadanie już nie istnieje. Odśwież zakładkę Zadania."],
  [/No document /, "📚 Tego dokumentu już nie ma w wiedzy. Odśwież zakładkę Wiedza."],
  [/'daily_limit' must be a whole number/, "✏️ Dzienny limit zapytań musi być liczbą całkowitą (albo zostaw puste)."],

  /* ----------------------------------------------------------------- form validation */
  [/'([^']+)' is required/, (m) => `✏️ Uzupełnij pole „${FIELD_NAMES[m[1]] || m[1]}”.`],
  [/(?:name|id) must match \[a-zA-Z0-9_-\](?:\{1,(\d+)\})?/,
    (m) => `✏️ Nazwa może zawierać tylko litery bez polskich znaków, cyfry, „-” i „_”${m[1] ? ` (maks. ${m[1]} znaków)` : ""}, bez spacji.`],
  [/must start with http:\/\/ or https:\/\//, "✏️ Adres musi zaczynać się od https:// (albo http:// dla serwera lokalnego)."],
  [/OpenAI-compatible provider needs a base_url/, "✏️ Podaj adres API dostawcy (np. https://api.openai.com/v1)."],
  [/Provider kind must be one of|protocol must be one of/, "✏️ Wybierz rodzaj z listy."],
  [/Provide 'text' or 'documents'|Each document needs a 'text'|Pusty plik/, "📚 Dodaj tekst albo plik z treścią – ten jest pusty."],
  [/A skill needs a description and instructions/, "🎓 Skill musi mieć opis i instrukcje."],
  [/Invalid parameter .*type must be one of/, "🧩 Parametr moda ma nieobsługiwany typ. Dozwolone: string, number, integer, boolean."],
  [/Unsupported HTTP method/, "🧩 Wybierz metodę HTTP z listy (GET, POST, PUT, PATCH, DELETE)."],
  [/Uszkodzony plik ZIP|Archiwum jest za duże po rozpakowaniu/, (m) => `🧠 ${m[0]}. Sprawdź, czy to właściwy plik eksportu (ZIP z ChatGPT lub Claude).`],
  [/Unknown retrieval mode/, "📚 Nieznany tryb wyszukiwania w bazie wiedzy."],

  /* --------------------------------------------------------------------- last resort */
  [/^[A-Z][A-Za-z]*(Error|Exception): /, "💥 Na serwerze wystąpił nieoczekiwany błąd. Spróbuj ponownie; jeśli się powtarza, skopiuj „Szczegóły” i zgłoś problem."],
];

const FIELD_NAMES = { name: "Nazwa", message: "Wiadomość", task: "Zadanie", goal: "Cel", url: "Adres", id: "Identyfikator",
  provider: "Dostawca", text: "Treść", query: "Zapytanie", instructions: "Instrukcje", description: "Opis", command: "Polecenie" };

/** Polish explanation for an error message, or null when it is not a known error. */
function explainError(msg) {
  const text = String(msg || "");
  if (!text) return null;
  for (const [pattern, message] of ERROR_RULES) {
    const m = text.match(pattern);
    if (m) return typeof message === "function" ? message(m, text) : message;
  }
  return null;
}

if (typeof module !== "undefined") module.exports = { explainError, ERROR_RULES };
