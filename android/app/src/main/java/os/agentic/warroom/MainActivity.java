package os.agentic.warroom;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.Uri;
import android.os.Bundle;
import android.text.InputType;
import android.view.KeyEvent;
import android.view.ViewGroup;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.Toast;

/**
 * Agentic OS for Android: the War Room in a full-screen WebView.
 *
 * The agents run on your own Agentic OS server (Oracle, Hetzner, OmGithub or Termux on this phone);
 * the app only stores that server's address. Hold the Back button to change it.
 */
public class MainActivity extends Activity {

    private static final String PREFS = "agentic_os";
    private static final String KEY_URL = "server_url";
    private static final String SETTINGS_LINK = "agentic-os://settings";
    private static final int FILE_CHOOSER_REQUEST = 1;

    private WebView webView;
    private ValueCallback<Uri[]> pendingUpload;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        webView = new WebView(this);
        FrameLayout root = new FrameLayout(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setContentView(root);
        configureWebView();

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else if (Friendly.parseAddress(serverUrl()).url == null) {
            askForServer(true); // nothing saved yet, or an address saved by an older version that cannot work
        } else {
            webView.loadUrl(serverUrl());
        }
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true); // the War Room keeps its login and chat sessions here
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        settings.setUserAgentString(settings.getUserAgentString() + " AgenticOSApp/1");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (SETTINGS_LINK.equals(url.toString())) {
                    askForServer(false);
                    return true;
                }
                Uri server = Uri.parse(serverUrl());
                if (url.getHost() != null && url.getHost().equals(server.getHost())) {
                    return false; // stay inside the app for the War Room itself
                }
                openExternally(url); // links to other sites open in the browser
                return true;
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    showOfflinePage(Friendly.networkError(error.getErrorCode(), String.valueOf(error.getDescription()), isOnline()));
                }
            }

            @Override
            public void onReceivedHttpError(WebView view, WebResourceRequest request, WebResourceResponse response) {
                String[] message = Friendly.httpError(response.getStatusCode());
                if (request.isForMainFrame() && message != null) {
                    showOfflinePage(message);
                }
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            // Lets the War Room upload files, e.g. a ChatGPT/Claude export for "Importuj pamięć".
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (pendingUpload != null) {
                    pendingUpload.onReceiveValue(null);
                }
                pendingUpload = callback;
                try {
                    startActivityForResult(params.createIntent(), FILE_CHOOSER_REQUEST);
                } catch (ActivityNotFoundException e) {
                    pendingUpload = null;
                    Toast.makeText(MainActivity.this, "Brak aplikacji do wyboru plików", Toast.LENGTH_LONG).show();
                    return false;
                }
                return true;
            }
        });
    }

    private String serverUrl() {
        return getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_URL, "");
    }

    /** Ask for the server address; on first launch the dialog cannot be dismissed without one. */
    private void askForServer(boolean firstRun) {
        EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setHint("np. https://twoj-serwer-8000.app.github.dev");
        input.setText(serverUrl());
        input.setSingleLine(true);
        int pad = (int) (20 * getResources().getDisplayMetrics().density);
        FrameLayout box = new FrameLayout(this);
        box.setPadding(pad, pad / 2, pad, 0);
        box.addView(input);

        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Adres Twojego Agentic OS")
                .setMessage("Wpisz adres serwera, na którym działa Agentic OS. "
                        + "Adres możesz później zmienić, przytrzymując przycisk Wstecz.")
                .setView(box)
                .setCancelable(!firstRun)
                .setPositiveButton("Połącz", null)
                .setNegativeButton(firstRun ? "Zamknij" : "Anuluj", (d, w) -> {
                    if (firstRun) {
                        finish();
                    }
                })
                .create();
        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            Friendly.Address address = Friendly.parseAddress(input.getText().toString());
            if (address.url == null) {
                input.setError(address.problem);
                return;
            }
            String url = address.url;
            getSharedPreferences(PREFS, MODE_PRIVATE).edit().putString(KEY_URL, url).apply();
            dialog.dismiss();
            webView.clearHistory();
            webView.loadUrl(url);
            if (firstRun) {
                Toast.makeText(this, "Przytrzymaj Wstecz, aby zmienić adres serwera", Toast.LENGTH_LONG).show();
            }
        }));
        dialog.show();
    }

    private boolean isOnline() {
        ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        return cm == null || cm.getActiveNetwork() != null;
    }

    /** A calm, themed page with what went wrong in plain Polish; never the raw "net::ERR_…" code. */
    private void showOfflinePage(String[] message) {
        String html = "<!doctype html><html lang=pl><head><meta name=viewport content='width=device-width,initial-scale=1'>"
                + "<meta name=color-scheme content='light dark'><style>"
                + ":root{--bg:#f5f6f4;--card:#fff;--text:#1a1d1c;--muted:#5f6763;--accent:#0f766e;--on:#fff;--line:#e1e4e0}"
                + "@media (prefers-color-scheme:dark){:root{--bg:#111413;--card:#1b1f1e;--text:#e9ecea;--muted:#9aa39e;"
                + "--accent:#2bb3a3;--on:#06201d;--line:#2f3633}}"
                + "body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,sans-serif;padding:40px 24px}"
                + "h1{font-size:26px;line-height:1.2;margin:0 0 12px;letter-spacing:-.4px}p{margin:0 0 10px;color:var(--muted)}"
                + "a{display:block;margin:14px 0 0;padding:15px;border-radius:16px;text-align:center;text-decoration:none;font-weight:700}"
                + ".go{background:var(--accent);color:var(--on)}.alt{background:var(--card);color:var(--text);border:1px solid var(--line)}"
                + "small{display:block;margin-top:22px;color:var(--muted);word-break:break-all}</style></head><body>"
                + "<h1>" + escape(message[0]) + "</h1>"
                + "<p>" + escape(message[1]) + "</p>"
                + "<a class=go href='" + escape(serverUrl()) + "'>Spróbuj ponownie</a>"
                + "<a class=alt href='" + SETTINGS_LINK + "'>Zmień adres serwera</a>"
                + "<small>Adres: " + escape(serverUrl()) + "</small>"
                + "</body></html>";
        webView.loadDataWithBaseURL(serverUrl(), html, "text/html", "utf-8", null);
    }

    private static String escape(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#39;").replace("\"", "&quot;");
    }

    private void openExternally(Uri url) {
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, url));
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Nie można otworzyć linku", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST && pendingUpload != null) {
            pendingUpload.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(resultCode, data));
            pendingUpload = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            event.startTracking(); // allows the long press below
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public boolean onKeyLongPress(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK) {
            askForServer(false);
            return true;
        }
        return super.onKeyLongPress(keyCode, event);
    }

    @Override
    public boolean onKeyUp(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && event.isTracking() && !event.isCanceled()) {
            if (webView.canGoBack()) {
                webView.goBack();
            } else {
                finish();
            }
            return true;
        }
        return super.onKeyUp(keyCode, event);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    protected void onDestroy() {
        webView.destroy();
        super.onDestroy();
    }
}
