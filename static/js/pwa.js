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

// Clear PWA badge if app is opened directly
if ('clearAppBadge' in navigator) {
    navigator.clearAppBadge().catch(e => console.log('Badge clear error', e));
}

// Intercept Native Install Prompt
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log('📱 [PWA] beforeinstallprompt event captured');

    // Show Install UI Banner & Navbar button
    const banner = document.getElementById('pwaInstallBanner');
    const navInstallBtn = document.getElementById('pwaNavInstallBtn');
    
    if (banner && !localStorage.getItem('pwa_dismissed')) {
        banner.style.display = 'flex';
    }
    if (navInstallBtn) {
        navInstallBtn.style.display = 'inline-flex';
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

// Trigger Install Action
window.triggerPWAInstall = async function () {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const choiceResult = await deferredPrompt.userChoice;
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted PWA installation');
        }
        deferredPrompt = null;
        const banner = document.getElementById('pwaInstallBanner');
        if (banner) banner.style.display = 'none';
    } else if (isIOS) {
        // Open iOS Instructions Modal
        const iosModal = document.getElementById('iosInstallModal');
        if (iosModal && typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(iosModal);
            modal.show();
        } else {
            alert("To install on iOS: Tap the Share icon (square with arrow) at the bottom and select 'Add to Home Screen'.");
        }
    } else {
        const uniModal = document.getElementById('universalInstallModal');
        if (uniModal && typeof bootstrap !== 'undefined') {
            const modal = new bootstrap.Modal(uniModal);
            modal.show();
        } else {
            showToastNotification('ℹ️ To install, select "Add to Home Screen" or "Install App" from your browser menu.');
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
    const bellBtn = document.getElementById('btnBellNotification');
    if (!bellBtn || !('Notification' in window) || !('serviceWorker' in navigator)) {
        return;
    }

    try {
        const reg = await navigator.serviceWorker.ready;
        const sub = await reg.pushManager.getSubscription();

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
    } catch (err) {
        console.warn('Subscription check error', err);
    }
}

document.addEventListener('DOMContentLoaded', checkPushSubscriptionState);

window.togglePushNotifications = async function () {
    const bellBtn = document.getElementById('btnBellNotification');

    if (!('Notification' in window)) {
        showToastNotification('⚠️ Push notifications are not supported on this browser.');
        return;
    }

    if (!('serviceWorker' in navigator)) {
        showToastNotification('⚠️ Service Worker is not available.');
        return;
    }

    try {
        const reg = await navigator.serviceWorker.ready;
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
        showToastNotification('⚠️ Push notification status: ' + e.message);
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
