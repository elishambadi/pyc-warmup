var staticCacheName = 'djangopwa-v2';
var filesToCache = [
    '/',
    '/offline/',  // Custom offline page
    '/static/css/style.css',  // Add your CSS file
    '/static/js/main.js',  // Add your JS file
    '/static/images/icons/pyc-logo.jpg',  // Add app icon
    // Add more static assets like fonts, icons, etc.
];

// Install event: Cache files
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(staticCacheName).then(function(cache) {
            return cache.addAll(filesToCache);
        })
    );
});

// Activate event: Clean up old caches
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cache) {
                    return cache !== staticCacheName;
                }).map(function(cache) {
                    return caches.delete(cache);
                })
            );
        })
    );
});

// Fetch event: Serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    var requestUrl = new URL(event.request.url);

    // Handle MP3 files and song pages
    if (requestUrl.pathname.startsWith('/songs/') || requestUrl.pathname.endsWith('.mp3')) {
        event.respondWith(
            caches.match(event.request).then(function(response) {
                return response || fetch(event.request).then(function(fetchResponse) {
                    return caches.open(staticCacheName).then(function(cache) {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                });
            }).catch(function() {
                return caches.match('/offline/');  // Fallback page
            })
        );
        return;
    }

    // Default caching strategy for other requests
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
