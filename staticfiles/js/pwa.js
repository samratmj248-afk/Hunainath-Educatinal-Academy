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

// Audio Chime Player for Admin Push Notifications
let notificationAudio = null;

function getNotificationAudio() {
    if (!notificationAudio) {
        notificationAudio = new Audio('/static/sounds/notification.wav');
        notificationAudio.preload = 'auto';
    }
    return notificationAudio;
}

// Unlock audio permission on user interaction so subsequent background/push events can play freely
function unlockAudioPlayback() {
    try {
        const audio = getNotificationAudio();
        // Play muted/briefly to prime the browser AudioContext & HTMLAudioElement
        audio.volume = 1.0;
        const playPromise = audio.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                audio.pause();
                audio.currentTime = 0;
                console.log('🔊 [PWA] Audio player primed & unlocked for admin notices.');
            }).catch(() => {
                // Ignore silent unlock aborts
            });
        }
    } catch (e) {
        // Safe failover
    }
}

// Ring chime sound function (Robust HTMLAudioElement + Web Audio API synthesizer fallback)
function playNoticeChimeSound() {
    let played = false;
    try {
        const audio = getNotificationAudio();
        audio.currentTime = 0;
        audio.volume = 1.0;
        const p = audio.play();
        if (p !== undefined) {
            p.then(() => {
                played = true;
                console.log('🔔 [PWA] Notification sound played successfully');
            }).catch(e => {
                console.warn('[PWA] Audio file play failed, triggering Web Audio fallback:', e);
                playWebAudioChimeFallback();
            });
        }
    } catch (err) {
        console.warn('[PWA] Audio error, using fallback:', err);
        playWebAudioChimeFallback();
    }
}

// Mobile Web Audio API fallback chime synthesizer (Guaranteed to play on iOS Safari & Android Chrome)
function playWebAudioChimeFallback() {
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const ctx = new AudioContext();
        if (ctx.state === 'suspended') {
            ctx.resume();
        }

        const playTone = (freq, start, duration) => {
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, ctx.currentTime + start);
            gain.gain.setValueAtTime(0.3, ctx.currentTime + start);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + duration);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start(ctx.currentTime + start);
            osc.stop(ctx.currentTime + start + duration);
        };

        // Dual harmonious school chime (E5 -> G#5 -> B5)
        playTone(659.25, 0, 0.4);
        playTone(830.61, 0.15, 0.4);
        playTone(987.77, 0.3, 0.6);
    } catch (e) {
        console.warn('[PWA] Web Audio fallback error:', e);
    }
}

// Listen for push notifications received from Service Worker while tab is open
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (event) => {
        // Trigger audio when an admin push notification arrives
        if (event.data && event.data.type === 'PLAY_NOTIFICATION_SOUND') {
            console.log('🔔 [PWA] Admin notification sound ringing for:', event.data.data ? event.data.data.title : 'Notice');
            playNoticeChimeSound();
        }
    });
}

// Clear PWA badge if app is opened directly
if ('clearAppBadge' in navigator) {
    navigator.clearAppBadge().catch(e => console.log('Badge clear error', e));
}

// Handle Native Install Prompt directly
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log('📱 [PWA] Native install prompt captured');

    // If page was loaded with ?install=1 or from QR, present direct install modal
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('install') === '1' || sessionStorage.getItem('pwa_qr_scan') === '1') {
        window.showDirectInstallModal();
    }
});

// Show Direct Install Modal (Interface in background, install prompt floating on top)
window.showDirectInstallModal = function () {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
    if (isStandalone) return;

    const modalEl = document.getElementById('pwaDirectInstallModal');
    if (!modalEl || typeof bootstrap === 'undefined') return;

    const isApple = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    const iosBox = document.getElementById('pwaIosGuideBox');
    const nativeBox = document.getElementById('pwaDirectInstallNativeBox');

    if (isApple) {
        if (iosBox) iosBox.style.display = 'block';
        if (nativeBox) nativeBox.style.display = 'none';
    } else {
        if (iosBox) iosBox.style.display = 'none';
        if (nativeBox) nativeBox.style.display = 'block';
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
};

// Auto-check on DOMContentLoaded for ?install=1
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('install') === '1') {
        sessionStorage.setItem('pwa_qr_scan', '1');
        // Wait a brief moment for interface to render in the background, then reveal modal
        setTimeout(() => {
            window.showDirectInstallModal();
        }, 600);
    }
});

// Direct Execute Install
window.executeDirectInstall = async function () {
    const modalEl = document.getElementById('pwaDirectInstallModal');
    if (modalEl && typeof bootstrap !== 'undefined') {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }

    if (deferredPrompt) {
        deferredPrompt.prompt();
        const choice = await deferredPrompt.userChoice;
        if (choice.outcome === 'accepted') {
            console.log('✅ PWA Install accepted');
        }
        deferredPrompt = null;
    } else {
        showToastNotification('📲 In your browser menu (⋮), tap "Add to Home Screen" or "Install App"');
    }
};

// App Installed Event - Automatically pop up installSuccessModal
window.addEventListener('appinstalled', () => {
    console.log('🎉 [PWA] App successfully installed!');
    const banner = document.getElementById('pwaInstallBanner');
    const navInstallBtn = document.getElementById('pwaNavInstallBtn');
    if (banner) banner.style.display = 'none';
    if (navInstallBtn) navInstallBtn.style.display = 'none';
    deferredPrompt = null;
    
    // Automatically display Success Popup
    const successModalEl = document.getElementById('installSuccessModal');
    if (successModalEl && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(successModalEl);
        modal.show();
    } else {
        showToastNotification('🎉 App Successfully Installed! Hunainath Academy is now on your home screen.');
    }
});

// Detect Environment & Device Capabilities
const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isAndroidDevice = /Android/i.test(navigator.userAgent);
const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;

// Trigger Install Action
window.triggerPWAInstall = async function () {
    // Hide mobile offcanvas drawer immediately
    const drawerEl = document.getElementById('mobileNavDrawer');
    if (drawerEl && typeof bootstrap !== 'undefined') {
        const drawerInstance = bootstrap.Offcanvas.getInstance(drawerEl);
        if (drawerInstance) drawerInstance.hide();
    }

    if (isStandaloneMode) {
        showToastNotification('✅ Hunainath Academy app is already installed and active!');
        return;
    }

    window.showDirectInstallModal();
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

        // Hide "Stay Notified Instantly" promo card and mobile drawer notification button if notifications are enabled
        const isNotifEnabled = (typeof Notification !== 'undefined' && Notification.permission === 'granted') || !!sub;
        document.querySelectorAll('.notification-promo-card, #noticePushAlertCard, .btn-drawer-notification, #drawerNotificationBtn').forEach(card => {
            if (isNotifEnabled) {
                card.style.display = 'none';
            } else {
                card.style.display = '';
            }
        });
    } catch (err) {
        console.warn('Subscription check error', err);
    }
}

document.addEventListener('DOMContentLoaded', checkPushSubscriptionState);

// Trigger Notification directly without confusing intermediary modal
window.openNotificationModal = async function () {
    await window.performPushSubscription();
};

window.togglePushNotifications = async function () {
    // Hide mobile offcanvas immediately if open
    const drawerEl = document.getElementById('mobileNavDrawer');
    if (drawerEl && typeof bootstrap !== 'undefined') {
        const drawerInstance = bootstrap.Offcanvas.getInstance(drawerEl);
        if (drawerInstance) {
            drawerInstance.hide();
        }
    }
    // Perform push subscription directly
    await window.performPushSubscription();
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

            // Immediately mark document and hide the enable button
            document.documentElement.classList.add('notifications-granted');
            document.querySelectorAll('.btn-drawer-notification, #drawerNotificationBtn').forEach(el => {
                el.style.setProperty('display', 'none', 'important');
                el.remove(); // Remove completely from the DOM
            });

            // Play instant confirmation chime sound
            unlockAudioPlayback();
            playNoticeChimeSound();
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

                // Immediately hide the enable notification button on mobile drawer
                document.querySelectorAll('.btn-drawer-notification, #drawerNotificationBtn').forEach(el => {
                    el.style.display = 'none';
                });

                // Immediately ring chime sound
                unlockAudioPlayback();
                setTimeout(() => {
                    playNoticeChimeSound();
                }, 100);
                
                // Automatically display the "Done!" popup modal
                const doneModalEl = document.getElementById('notificationDoneModal');
                if (doneModalEl && typeof bootstrap !== 'undefined') {
                    const doneModal = new bootstrap.Modal(doneModalEl);
                    doneModal.show();
                } else {
                    showToastNotification('🔔 Done! Notifications enabled! Chime sound rung.');
                }
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
