package os.agentic.warroom;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class FriendlyTest {

    @Test
    public void fixesCommonAddressTypos() {
        assertEquals("https://my-8000.app.github.dev/", Friendly.parseAddress("https://https:\\\\my-8000.app.github.dev").url);
        assertEquals("https://my-8000.app.github.dev/", Friendly.parseAddress("https:/my-8000.app.github.dev").url);
        assertEquals("https://example.com/", Friendly.parseAddress(" example.com ").url);
        assertEquals("http://localhost:8000/", Friendly.parseAddress("localhost:8000").url);
    }

    @Test
    public void explainsAddressesThatCannotWork() {
        for (String raw : new String[] {"", "a b", "foo", "http://0.0.0.0:8000", "https://0.0.0.0:8080", "https:\\\\1-2-3-4.sslip.io"}) {
            Friendly.Address a = Friendly.parseAddress(raw);
            assertNull(raw, a.url);
            assertNotNull(raw, a.problem);
        }
    }

    @Test
    public void networkErrorsNeverShowRawCodes() {
        assertTrue(Friendly.networkError(-1, "net::ERR_CLEARTEXT_NOT_PERMITTED", true)[1].contains("https://"));
        assertEquals("Brak internetu", Friendly.networkError(-2, "net::ERR_NAME_NOT_RESOLVED", false)[0]);
        for (int code : new int[] {-2, -6, -7, -8, -10, -11, -12, -1}) {
            String[] message = Friendly.networkError(code, "net::ERR_SOMETHING", true);
            assertFalse(message[0].contains("ERR_") || message[1].contains("ERR_"));
        }
    }

    @Test
    public void httpErrorsOnlyReplaceBrokenPages() {
        assertNull(Friendly.httpError(200));
        assertNotNull(Friendly.httpError(502));
        assertNotNull(Friendly.httpError(404));
    }
}
