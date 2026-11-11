const CACHE_NAME = 'release-rydar-v2';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './releases.json',
    './manifest.json'
];

// Install event: cache core assets
self.addEventListener('install', (event) => {
    self.skipWaiting(); // Force the waiting service worker to become active
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate event: clean up old caches immediately
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event: network-first for JSON, cache-first for static assets
self.addEventListener('fetch', (event) => {
    if (event.request.url.includes('releases.json')) {
        // Always fetch fresh releases.json from network so updates show instantly
        event.respondWith(
            fetch(event.request)
                .then((networkResponse) => {
                    return caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, networkResponse.clone());
                        return networkResponse;
                    });
                })
                .catch(() => caches.match(event.request))
        );
    } else {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                return cachedResponse || fetch(event.request);
            })
        );
    }
});
