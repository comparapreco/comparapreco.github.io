const CACHE_NAME = 'radar-pwa-v10';
const ROOT = self.registration.scope;
const CORE_ASSETS = [
  ROOT,
  ROOT + 'index.html',
  ROOT + 'minha-lista/',
  ROOT + 'recomendados/',
  ROOT + 'alertas/',
  ROOT + 'pro/',
  ROOT + 'academia/',
  ROOT + 'exclusivos/',
  ROOT + 'radar-index/',
  ROOT + 'inteligencia/',
  ROOT + 'newsletter/',
  ROOT + 'imprensa/',
  ROOT + 'parcerias/',
  ROOT + 'midia-kit/',
  ROOT + 'assets/css/style.css',
  ROOT + 'assets/js/app.js',
  ROOT + 'assets/js/firebase-config.js',
  ROOT + 'assets/js/radar-auth.js',
  ROOT + 'assets/js/pwa.js',
  ROOT + 'data/products/offers.json',
  ROOT + 'data/retention/newsletter-daily.json',
  ROOT + 'data/retention/admin-metrics.json',
  ROOT + 'data/radar-index.json',
  ROOT + 'data/market-intelligence.json',
  ROOT + 'data/revenue-metrics.json',
  ROOT + 'data/segmented-newsletter.json',
  ROOT + 'data/editorial-automation.json',
  ROOT + 'manifest.webmanifest',
  ROOT + 'assets/icons/icon-192.png',
  ROOT + 'assets/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      }).catch(() => caches.match(request).then(cached => cached || caches.match(ROOT + 'index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(response => {
      if (!response || response.status !== 200 || response.type === 'opaque') return response;
      const copy = response.clone();
      caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
      return response;
    }).catch(() => cached))
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification?.data?.url || ROOT + 'minha-lista/';
  event.waitUntil(clients.openWindow(url));
});
