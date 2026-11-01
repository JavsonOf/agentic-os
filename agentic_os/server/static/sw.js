/* Agentic OS service worker: caches the app shell so it opens like an app; API calls always go to the network. */
const CACHE = "aos-shell-v17";
const SHELL = ["/", "/app.js", "/errors.js", "/qr.js", "/app.css", "/icon.svg", "/icon-192.png", "/manifest.webmanifest", "/wake.html"];
// A server that does not answer (a sleeping Codespace replies 404, a proxy 502-504) gets the "Serwer śpi" screen.
const ASLEEP = new Set([404, 502, 503, 504]);

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin) return;
  if (event.request.mode === "navigate") {
    event.respondWith(
      fetch(event.request)
        .then((res) => {
          if (ASLEEP.has(res.status)) return caches.match("/wake.html").then((page) => page || res);
          if (res.ok && SHELL.includes(url.pathname)) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(event.request, copy)); }
          return res;
        })
        .catch(() => caches.match(event.request).then((page) => page || caches.match("/wake.html")))
    );
    return;
  }
  if (!SHELL.includes(url.pathname)) return;
  // Network first so updates show up immediately; fall back to the cached shell when offline.
  event.respondWith(
    fetch(event.request)
      .then((res) => { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(event.request, copy)); return res; })
      .catch(() => caches.match(event.request))
  );
});
// "Powiadomienia o prośbach": tapping the notification opens (or focuses) the War Room.
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
    const open = list.find((c) => new URL(c.url).origin === location.origin);
    return open ? open.focus() : self.clients.openWindow("/");
  }));
});
