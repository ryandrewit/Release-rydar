const CACHE_NAME = 'release-rydar-v10';
const ASSETS_TO_CACHE = [
    './',
    './index.html',
    './releases.json',
    './manifest.json'
];

// Install event: cache core assets and skip waiting
self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate event: clean up stale legacy caches immediately
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

// Fetch event handling
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // 1. CRITICAL: Let all Supabase cloud database requests go straight to the network
    if (url.hostname.includes('supabase.co')) {
        return; 
    }

    // 2. Network-first strategy for releases.json so schedule updates show instantly
    if (url.pathname.endsWith('releases.json')) {
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
        return;
    }

    // 3. Cache-first strategy for static app assets (HTML, icons, manifests)
    event.respondWith(
        caches.match(event.request).then((cachedResponse) => {
            return cachedResponse || fetch(event.request);
        })
    );
});
