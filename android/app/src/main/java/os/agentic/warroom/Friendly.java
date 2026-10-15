package os.agentic.warroom;

import java.net.URI;
import java.util.Locale;

/**
 * Plain-Polish messages for everything that can go wrong before the War Room loads: a mistyped server address
 * and the WebView's network errors. Pure Java (no Android classes) so it can be unit-tested anywhere.
 */
final class Friendly {

    /** Normalised address, or null with {@link #problem} set to what to tell the user. */
    static final class Address {
        final String url;
        final String problem;

        Address(String url, String problem) {
            this.url = url;
            this.problem = problem;
        }
    }

    private Friendly() {
    }

    /** Accepts "1.2.3.4:8000", "example.com", full URLs and common typos (backslashes, a doubled "https://"). */
    static Address parseAddress(String raw) {
        String url = raw == null ? "" : raw.trim().replace('\\', '/');
        if (url.isEmpty()) {
            return new Address(null, "Wpisz adres serwera.");
        }
        if (url.contains(" ")) {
            return new Address(null, "Adres nie może zawierać spacji.");
        }
        // "https://https://…" or "https:/https:/…" after pasting twice: keep only the last scheme.
        String lower = url.toLowerCase(Locale.ROOT);
        int last = Math.max(lower.lastIndexOf("http://"), lower.lastIndexOf("https://"));
        if (last > 0) {
            url = url.substring(last);
        } else {
            url = url.replaceFirst("(?i)^(https?):/+", "$1://");
        }
        if (!url.matches("(?i)^https?://.*")) {
            boolean local = url.startsWith("localhost") || url.startsWith("127.0.0.1");
            url = (local ? "http://" : "https://") + url;
        }
        String host;
        try {
            host = new URI(url).getHost();
        } catch (Exception e) {
            host = null;
        }
        if (host == null || host.isEmpty() || !host.contains(".") && !host.equals("localhost")) {
            return new Address(null, "To nie wygląda na adres serwera. Przykład: https://twoj-serwer-8000.app.github.dev");
        }
        if (host.equals("0.0.0.0")) {
            return new Address(null, "0.0.0.0 to adres, na którym serwer nasłuchuje, a nie adres do otwarcia. "
                    + "Wpisz adres z Codespaces (…-8000.app.github.dev) albo swojego serwera.");
        }
        if (host.equals("1-2-3-4.sslip.io")) {
            return new Address(null, "To tylko przykład. Wpisz prawdziwy adres swojego serwera.");
        }
        return new Address(url.endsWith("/") ? url : url + "/", null);
    }

    /** Title and explanation for a WebView error, never the raw "net::ERR_…" code. */
    static String[] networkError(int code, String description, boolean online) {
        String d = description == null ? "" : description.toUpperCase(Locale.ROOT);
        if (!online) {
            return new String[] {"Brak internetu", "Telefon nie ma połączenia z internetem. Włącz Wi-Fi lub dane komórkowe i spróbuj ponownie."};
        }
        if (d.contains("CLEARTEXT")) {
            return new String[] {"Niezabezpieczony adres", "Ten adres zaczyna się od http://. Aplikacja łączy się tylko przez bezpieczne https:// – zmień adres na https://…"};
        }
        switch (code) {
            case -2: // ERROR_HOST_LOOKUP
                return new String[] {"Nie znaleziono serwera", "Pod tym adresem nie ma serwera. Sprawdź, czy adres jest wpisany dokładnie tak, jak w Codespaces lub na Twoim serwerze."};
            case -6: // ERROR_CONNECT
            case -7: // ERROR_IO
                return new String[] {"Serwer nie odpowiada", "Adres jest poprawny, ale Agentic OS pod nim nie działa. Uruchom serwer (agentic-os serve) i spróbuj ponownie."};
            case -8: // ERROR_TIMEOUT
                return new String[] {"Serwer odpowiada zbyt długo", "Połączenie trwało za długo. Sprawdź internet albo czy serwer nie jest przeciążony."};
            case -11: // ERROR_FAILED_SSL_HANDSHAKE
                return new String[] {"Problem z bezpiecznym połączeniem", "Nie udało się nawiązać bezpiecznego połączenia (HTTPS) z serwerem. Sprawdź adres albo certyfikat serwera."};
            case -12: // ERROR_BAD_URL
            case -10: // ERROR_UNSUPPORTED_SCHEME
                return new String[] {"Nieprawidłowy adres", "Tego adresu nie da się otworzyć. Zmień go na adres zaczynający się od https://"};
            default:
                return new String[] {"Brak połączenia z Agentic OS", "Nie udało się połączyć z serwerem. Sprawdź internet i czy serwer działa."};
        }
    }

    /** Explanation for an HTTP error page of the War Room itself, or null to show the page as is. */
    static String[] httpError(int status) {
        if (status == 502 || status == 503 || status == 504) {
            return new String[] {"Serwer jest wyłączony", "Adres działa, ale Agentic OS jest zatrzymany (np. Codespace uśpił się). Uruchom go ponownie: agentic-os serve."};
        }
        if (status >= 500) {
            return new String[] {"Błąd serwera", "Serwer Agentic OS zgłosił błąd. Spróbuj ponownie za chwilę."};
        }
        if (status == 404) {
            return new String[] {"Nie ma tu Agentic OS", "Pod tym adresem działa coś innego. Sprawdź, czy to adres War Room (port 8000)."};
        }
        return null;
    }
}
