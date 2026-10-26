/**
 * Shree Hunainath Educational Academy - PWA & Web Push Notifications
 */

let deferredPrompt = null;
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;

// Register Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => {
                console.log('✅ [PWA] Service Worker registered with scope:', reg.scope);
            })
            .catch(err => {
                console.warn('[PWA] Service Worker registration failed:', err);
            });
    });
}

// Audio Chime Player for Notifications
const notificationAudio = new Audio('/static/sounds/notification.wav');
notificationAudio.preload = 'auto';

// Unlock Web Audio context / Audio element on first user gesture
function unlockNotificationAudio() {
    notificationAudio.play().then(() => {
        notificationAudio.pause();
        notificationAudio.currentTime = 0;
    }).catch(() => {});
    document.removeEventListener('click', unlockNotificationAudio);
    document.removeEventListener('touchstart', unlockNotificationAudio);
}
document.addEventListener('click', unlockNotificationAudio, { once: true });
document.addEventListener('touchstart', unlockNotificationAudio, { once: true });

// Listen for push notifications received from Service Worker while tab is open
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
            console.log('🔔 [PWA] Notification sound triggered by push event');
            try {
                notificationAudio.currentTime = 0;
                notificationAudio.play().catch(e => {
                    console.warn('[PWA] Autoplay audio error:', e);
                });
            } catch (err) {
                console.error('[PWA] Audio error:', err);
            }
        }
    });
}

// Clear PWA badge if app is opened directly
if ('clearAppBadge' in navigator) {
    navigator.clearAppBadge().catch(e => console.log('Badge clear error', e));
}

// Intercept Native Install Prompt
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log('📱 [PWA] beforeinstallprompt event captured');

    // Only present installation prompts/banners on mobile or handheld devices (screen width <= 768px or touch mobile)
    const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
    const banner = document.getElementById('pwaInstallBanner');
    
    if (isMobileDevice && banner && !localStorage.getItem('pwa_dismissed')) {
        banner.style.display = 'flex';
    }
});

// App Installed Event
window.addEventListener('appinstalled', () => {
    console.log('🎉 [PWA] App successfully installed!');
    const banner = document.getElementById('pwaInstallBanner');
    const navInstallBtn = document.getElementById('pwaNavInstallBtn');
    if (banner) banner.style.display = 'none';
    if (navInstallBtn) navInstallBtn.style.display = 'none';
    deferredPrompt = null;
    showToastNotification('🎉 Hunainath Academy app is now installed on your device!');
});

// Detect Environment & Device Capabilities
const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isAndroidDevice = /Android/i.test(navigator.userAgent);
const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

// Trigger Install Action (Universal for Android, Chrome, Edge, Safari, iOS, Windows, Mac)
window.triggerPWAInstall = async function () {
    if (isStandaloneMode) {
        showToastNotification('✅ Hunainath Academy app is already installed and active!');
        return;
    }

    if (deferredPrompt) {
        // Native prompt supported (Chrome, Edge, Android Chrome, Samsung Internet)
        deferredPrompt.prompt();
        const choiceResult = await deferredPrompt.userChoice;
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted PWA installation');
        }
        deferredPrompt = null;
        const banner = document.getElementById('pwaInstallBanner');
        if (banner) banner.style.display = 'none';
    } else if (isIOSDevice) {
        // iOS Safari manual install modal
        const iosModal = document.getElementById('iosInstallModal');
        if (iosModal && typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(iosModal);
            modal.show();
        } else {
            alert("To install on iPhone/iPad: Tap the Share button in Safari, then tap 'Add to Home Screen'.");
        }
    } else {
        // Universal modal for all browsers where beforeinstallprompt was already fired, or browser menu is used
        const uniModal = document.getElementById('universalInstallModal');
        if (uniModal && typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(uniModal);
            modal.show();
        } else {
            showToastNotification('ℹ️ Tap your browser menu (⋮) and select "Install App" or "Add to Home Screen".');
        }
    }
};

window.dismissPwaBanner = function () {
    const banner = document.getElementById('pwaInstallBanner');
    if (banner) banner.style.display = 'none';
    localStorage.setItem('pwa_dismissed', 'true');
};

// ==============================================================================
// WEB PUSH NOTIFICATION SUBSCRIBER
// ==============================================================================

async function checkPushSubscriptionState() {
    const bellBtns = document.querySelectorAll('.btn-bell-toggle');
    if (!('Notification' in window) || !('serviceWorker' in navigator)) {
        return;
    }

    try {
        const reg = await navigator.serviceWorker.ready;
        if (!reg.pushManager) return;
        const sub = await reg.pushManager.getSubscription();

        if (!sub && Notification.permission === 'granted') {
            try {
                const resKey = await fetch('/api/push/vapid-key/');
                const dataKey = await resKey.json();
                if (dataKey.publicKey) {
                    const appServerKey = urlBase64ToUint8Array(dataKey.publicKey);
                    sub = await reg.pushManager.subscribe({
                        userVisibleOnly: true,
                        applicationServerKey: appServerKey
                    });
                    await fetch('/api/push/subscribe/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(sub.toJSON())
                    });
                    console.log('✅ [PWA] Auto-subscribed on permission granted');
                }
            } catch (autoSubErr) {
                console.warn('[PWA] Auto-subscribe error:', autoSubErr);
            }
        } else if (sub) {
            // Validate if active subscription matches current server VAPID key
            try {
                const resKey = await fetch('/api/push/vapid-key/');
                const dataKey = await resKey.json();
                if (dataKey.publicKey) {
                    const serverKeyBytes = urlBase64ToUint8Array(dataKey.publicKey);
                    const subKeyBuffer = sub.options && sub.options.applicationServerKey;
                    let isMatch = true;
                    if (subKeyBuffer) {
                        const subKeyBytes = new Uint8Array(subKeyBuffer);
                        isMatch = serverKeyBytes.length === subKeyBytes.length;
                        if (isMatch) {
                            for (let i = 0; i < serverKeyBytes.length; i++) {
                                if (serverKeyBytes[i] !== subKeyBytes[i]) {
                                    isMatch = false;
                                    break;
                                }
                            }
                        }
                    }
                    if (!isMatch) {
                        console.log('🔄 [PWA] Refreshing stale VAPID subscription...');
                        await sub.unsubscribe();
                        sub = await reg.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: serverKeyBytes
                        });
                    }
                    // Always ensure current subscription is registered in server database
                    await fetch('/api/push/subscribe/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(sub.toJSON())
                    });
                    console.log('✅ [PWA] Subscription verified and synced with server database');
                }
            } catch (vapidCheckErr) {
                console.warn('[PWA] Key validation error:', vapidCheckErr);
            }
        }

        bellBtns.forEach(bellBtn => {
            if (sub) {
                bellBtn.classList.add('subscribed');
                bellBtn.title = 'Push Notifications Enabled (Click to disable)';
                const icon = bellBtn.querySelector('i');
                if (icon) icon.className = 'fas fa-bell text-warning';
            } else {
                bellBtn.classList.remove('subscribed');
                bellBtn.title = 'Enable Push Notifications';
                const icon = bellBtn.querySelector('i');
                if (icon) icon.className = 'far fa-bell';
            }
        });
    } catch (err) {
        console.warn('Subscription check error', err);
    }
}

document.addEventListener('DOMContentLoaded', checkPushSubscriptionState);

// Trigger Notification Modal
window.openNotificationModal = async function () {
    const modalEl = document.getElementById('enableNotificationModal');
    if (!modalEl || typeof bootstrap === 'undefined') {
        performPushSubscription();
        return;
    }

    // Check if already subscribed
    try {
        if ('serviceWorker' in navigator && 'Notification' in window) {
            const reg = await navigator.serviceWorker.ready;
            if (reg.pushManager) {
                const sub = await reg.pushManager.getSubscription();
                const btn = document.getElementById('btnConfirmEnablePush');
                if (sub) {
                    if (btn) {
                        btn.innerHTML = '<i class="fas fa-bell-slash"></i> <span>Disable Notifications</span>';
                        btn.classList.add('btn-modal-danger');
                    }
                } else {
                    if (btn) {
                        btn.innerHTML = '<i class="fas fa-bell"></i> <span>Enable Notifications Now</span>';
                        btn.classList.remove('btn-modal-danger');
                    }
                }
            }
        }
    } catch (e) {}

    const modal = new bootstrap.Modal(modalEl);
    modal.show();
};

window.togglePushNotifications = function () {
    window.openNotificationModal();
};

window.performPushSubscription = async function () {
    // Dismiss the modal first if open
    const modalEl = document.getElementById('enableNotificationModal');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) modalInstance.hide();
    }

    // 1. Check browser and context compatibility
    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        showToastNotification('⚠️ Push notifications require a secure connection (HTTPS).');
        return;
    }

    if (!('Notification' in window)) {
        if (isIOSDevice && !isStandaloneMode) {
            showToastNotification('📲 On iPhone/iPad: Please install the app first to your Home Screen to enable Push Notifications.');
            window.triggerPWAInstall();
            return;
        }
        showToastNotification('⚠️ Push notifications are not supported on this browser.');
        return;
    }

    if (!('serviceWorker' in navigator)) {
        showToastNotification('⚠️ Service Worker is not available.');
        return;
    }

    try {
        const reg = await navigator.serviceWorker.ready;
        if (!reg.pushManager) {
            showToastNotification('⚠️ Push messaging is not supported by your current browser.');
            return;
        }

        let sub = await reg.pushManager.getSubscription();

        if (sub) {
            // Unsubscribe
            await sub.unsubscribe();
            await fetch('/api/push/unsubscribe/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ endpoint: sub.endpoint })
            });

            checkPushSubscriptionState();
            showToastNotification('🔕 Push notifications turned off.');
        } else {
            // Check if already explicitly denied by user
            if (Notification.permission === 'denied') {
                showNotificationRecoveryModal();
                return;
            }

            // Request permission
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                showNotificationRecoveryModal();
                return;
            }

            // Get VAPID public key
            const resKey = await fetch('/api/push/vapid-key/');
            const dataKey = await resKey.json();

            if (!dataKey.publicKey) {
                showToastNotification('⚠️ Push notification keys are not configured.');
                return;
            }

            const appServerKey = urlBase64ToUint8Array(dataKey.publicKey);
            sub = await reg.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: appServerKey
            });

            // Save subscription to server
            const saveRes = await fetch('/api/push/subscribe/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(sub.toJSON())
            });

            const result = await saveRes.json();
            if (result.status === 'success') {
                checkPushSubscriptionState();
                showToastNotification('🔔 Notifications enabled! You will receive urgent notices instantly.');
            }
        }
    } catch (e) {
        console.error('Push error:', e);
        showToastNotification('⚠️ ' + (e.message || 'Notification setup error'));
    }
};

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

function showNotificationRecoveryModal() {
    const modalEl = document.getElementById('notifRecoveryModal');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    } else {
        showToastNotification('⚠️ Notifications blocked. Please tap the lock icon in your browser address bar to allow.');
    }
}

function showToastNotification(msg) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 85px;
        left: 50%;
        transform: translateX(-50%);
        background: #0A1128;
        color: #ffffff;
        padding: 12px 24px;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 600;
        z-index: 10000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        border: 1px solid rgba(245, 158, 11, 0.4);
        display: flex;
        align-items: center;
        gap: 10px;
        animation: fadeIn 0.3s ease;
    `;
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}
