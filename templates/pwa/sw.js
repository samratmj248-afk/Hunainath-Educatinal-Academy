// ==============================================================================
// SERVICE WORKER - SHREE HUNAINATH EDUCATIONAL ACADEMY
// Offline Cache Management, Resilient Fallback & Web Push Notifications
// ==============================================================================

const CACHE_NAME = 'hunainath-pwa-v1.0.3';
const STATIC_ASSETS = [
    '/',
    '/offline/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/images/logo.png',
    '/static/images/icons/icon-192x192.png',
    '/static/sounds/notification.wav',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// Install Event: Resilient Pre-cache of static shells
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[SW] Pre-caching offline essentials');
            return Promise.allSettled(
                STATIC_ASSETS.map((url) =>
                    cache.add(url).catch((err) => console.warn('[SW] Cache item skipped:', url, err))
                )
            );
        }).then(() => self.skipWaiting())
    );
});

// Activate Event: Clean up outdated caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[SW] Deleting obsolete cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch Event: Network-first for pages, cache-first for assets
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // Ignore non-GET requests or admin URLs
    if (request.method !== 'GET' || request.url.includes('/admin/')) {
        return;
    }

    // HTML Page navigations
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Update cache copy dynamically
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                    return response;
                })
                .catch(async () => {
                    // Try cache, fallback to offline template
                    const cachedResponse = await caches.match(request);
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    return caches.match('/offline/');
                })
        );
        return;
    }

    // Static Assets & Images: Stale-While-Revalidate
    event.respondWith(
        caches.match(request).then((cachedResponse) => {
            const fetchPromise = fetch(request).then((networkResponse) => {
                if (networkResponse && networkResponse.status === 200) {
                    const clone = networkResponse.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
                }
                return networkResponse;
            }).catch(() => {/* Offline fallback */});

            return cachedResponse || fetchPromise;
        })
    );
});

// ==============================================================================
// WEB PUSH NOTIFICATIONS
// ==============================================================================

self.addEventListener('push', (event) => {
    let data = {
        title: 'Hunainath Educational Academy Notice',
        body: 'New urgent announcement published. Tap to view details.',
        url: '/notices/',
        icon: '/static/images/icons/icon-192x192.png',
        badge: '/static/images/icons/icon-72x72.png',
        sound: '/static/sounds/notification.wav'
    };

    if (event.data) {
        try {
            data = Object.assign(data, event.data.json());
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body: data.body,
        icon: data.icon || '/static/images/icons/icon-192x192.png',
        badge: data.badge || '/static/images/icons/icon-72x72.png',
        vibrate: [250, 100, 250, 100, 250],
        sound: data.sound || '/static/sounds/notification.wav',
        requireInteraction: true,
        data: {
            url: data.url || '/'
        },
        actions: [
            { action: 'open', title: 'View Details' },
            { action: 'close', title: 'Dismiss' }
        ],
        tag: 'hunainath-broadcast-' + Date.now()
    };

    // Broadcast chime to active window tabs and display push notification concurrently
    const notifyClientsPromise = self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
        windowClients.forEach((client) => {
            client.postMessage({
                type: 'PLAY_NOTIFICATION_SOUND',
                data: data
            });
        });
    }).catch((e) => console.warn('[SW] Client message error:', e));

    const showNotifPromise = self.registration.showNotification(data.title, options);

    event.waitUntil(
        Promise.all([notifyClientsPromise, showNotifPromise])
    );
});

// Notification Click Event
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'close') {
        return;
    }

    const targetUrl = (event.notification.data && event.notification.data.url) || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
            for (let client of windowClients) {
                if (client.url.includes(targetUrl) && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});
