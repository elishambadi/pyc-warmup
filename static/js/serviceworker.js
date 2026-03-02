var staticCacheName = 'djangopwa-v3';
var dynamicCacheName = 'djangopwa-dynamic-v3';
var filesToCache = [
    '/',
    '/songs/',
    '/offline/',
    '/static/images/icons/pyc-logo.jpg',
];

// Install event: Cache core files
self.addEventListener('install', function(event) {
    console.log('[ServiceWorker] Installing...');
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache) {
            console.log('[ServiceWorker] Caching app shell');
            return cache.addAll(filesToCache);
        })
    );
    self.skipWaiting();
});

// Activate event: Clean up old caches
self.addEventListener('activate', function(event) {
    console.log('[ServiceWorker] Activating...');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cache) {
                    return cache !== staticCacheName && cache !== dynamicCacheName;
                }).map(function(cache) {
                    console.log('[ServiceWorker] Removing old cache:', cache);
                    return caches.delete(cache);
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch event: Network first for songs and MP3s, cache as fallback
self.addEventListener('fetch', function(event) {
    var requestUrl = new URL(event.request.url);
    
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Handle song pages - Cache first, update in background
    if (requestUrl.pathname.startsWith('/songs/') && !requestUrl.pathname.includes('/add')) {
        event.respondWith(
            caches.match(event.request).then(function(response) {
                var fetchPromise = fetch(event.request).then(function(networkResponse) {
                    if (networkResponse && networkResponse.status === 200) {
                        return caches.open(dynamicCacheName).then(function(cache) {
                            cache.put(event.request, networkResponse.clone());
                            return networkResponse;
                        });
                    }
                    return networkResponse;
                });
                
                return response || fetchPromise;
            }).catch(function() {
                return caches.match('/offline/');
            })
        );
        return;
    }

    // Handle MP3 files and media - Cache first for faster playback
    if (requestUrl.pathname.includes('/media/') && (requestUrl.pathname.endsWith('.mp3') || requestUrl.pathname.endsWith('.mp4'))) {
        event.respondWith(
            caches.match(event.request).then(function(response) {
                if (response) {
                    console.log('[ServiceWorker] Serving MP3 from cache:', requestUrl.pathname);
                    return response;
                }
                
                console.log('[ServiceWorker] Fetching and caching MP3:', requestUrl.pathname);
                return fetch(event.request).then(function(fetchResponse) {
                    if (fetchResponse && fetchResponse.status === 200) {
                        return caches.open(dynamicCacheName).then(function(cache) {
                            cache.put(event.request, fetchResponse.clone());
                            return fetchResponse;
                        });
                    }
                    return fetchResponse;
                }).catch(function() {
                    console.log('[ServiceWorker] MP3 fetch failed:', requestUrl.pathname);
                });
            })
        );
        return;
    }

    // Default: Network first, fallback to cache
    event.respondWith(
        fetch(event.request).then(function(response) {
            if (response && response.status === 200 && requestUrl.origin === location.origin) {
                return caches.open(dynamicCacheName).then(function(cache) {
                    cache.put(event.request, response.clone());
                    return response;
                });
            }
            return response;
        }).catch(function() {
            return caches.match(event.request).then(function(response) {
                return response || caches.match('/offline/');
            });
        })
    );
});
