/* PyTrainer service worker: makes the app installable and lets it open without the network.

   The server fills in VERSION and the list of files (see _service_worker in server.py), so a new
   release installs a fresh cache. Files are fetched from the network first, so a `git pull` shows
   up on the next load; the cache is only the fallback when the server can't be reached. The API
   is never cached: your progress always comes from the server. */
const VERSION = "__VERSION__";
const SHELL = ["__SHELL__"];
const CACHE = `pytrainer-${VERSION}`;

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys()
    .then((keys) => Promise.all(keys.filter((k) => k.startsWith("pytrainer-") && k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin || url.pathname.startsWith("/api/")) return;
  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const res = await fetch(req);
      if (res.ok) cache.put(req, res.clone());
      return res;
    } catch (err) {
      // Offline: the cached file, and for a page load the cached app shell.
      const hit = await cache.match(req, { ignoreSearch: true }) || (req.mode === "navigate" ? await cache.match("./") : null);
      if (hit) return hit;
      throw err;
    }
  })());
});
