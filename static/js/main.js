/**
 * Shree Hunainath Educational Academy - Frontend Interactions & Animations
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Sticky Header Scroll Effect
    const header = document.querySelector('header.sticky-nav');
    const scrollTopBtn = document.getElementById('btnScrollTop');

    window.addEventListener('scroll', () => {
        const scrolled = window.scrollY > 40;
        if (header) {
            header.classList.toggle('scrolled', scrolled);
        }
        if (scrollTopBtn) {
            scrollTopBtn.classList.toggle('visible', window.scrollY > 350);
        }
    });

    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 2. Animated Counter Elements
    const counters = document.querySelectorAll('.counter-val');
    if (counters.length > 0 && 'IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const counter = entry.target;
                    const target = parseInt(counter.getAttribute('data-target'), 10) || 0;
                    const duration = 1800; // ms
                    const startTime = performance.now();

                    const updateCount = (currentTime) => {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        // Ease out quad
                        const easeProgress = 1 - (1 - progress) * (1 - progress);
                        const currentVal = Math.floor(easeProgress * target);

                        counter.textContent = currentVal.toLocaleString();

                        if (progress < 1) {
                            requestAnimationFrame(updateCount);
                        } else {
                            counter.textContent = target.toLocaleString();
                        }
                    };

                    requestAnimationFrame(updateCount);
                    observer.unobserve(counter);
                }
            });
        }, { threshold: 0.3 });

        counters.forEach(c => counterObserver.observe(c));
    }

    // 3. Category Filter Tabs (Programs & Gallery)
    const filterButtons = document.querySelectorAll('.filter-tab-btn');
    const filterItems = document.querySelectorAll('.filterable-card');

    if (filterButtons.length > 0) {
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                filterButtons.forEach(b => b.classList.remove('active', 'btn-primary'));
                filterButtons.forEach(b => b.classList.add('btn-outline-secondary'));

                btn.classList.add('active', 'btn-primary');
                btn.classList.remove('btn-outline-secondary');

                const targetCategory = btn.getAttribute('data-filter');

                filterItems.forEach(item => {
                    const itemCat = item.getAttribute('data-category');
                    if (targetCategory === 'ALL' || itemCat === targetCategory) {
                        item.style.display = 'block';
                        item.classList.add('fade-in-item');
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // 4. Button Ripple Click Effect
    document.querySelectorAll('.btn-ripple').forEach(button => {
        button.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-wave');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - size / 2}px`;
            ripple.style.top = `${e.clientY - rect.top - size / 2}px`;
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 5. Auto Dismiss Flash Messages after 5 seconds
    const flashAlerts = document.querySelectorAll('.alert-dismissible');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            try {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            } catch (e) {
                alert.style.display = 'none';
            }
        }, 5000);
    });

    // 6. Mobile Offcanvas Backdrop & Body Scroll Lock
    const mobileDrawer = document.getElementById('mobileNavDrawer');
    if (mobileDrawer) {
        mobileDrawer.addEventListener('show.bs.offcanvas', function () {
            document.body.classList.add('drawer-open-lock');
            document.documentElement.style.overflow = 'hidden';
            document.body.style.overflow = 'hidden';
        });
        mobileDrawer.addEventListener('hidden.bs.offcanvas', function () {
            document.body.classList.remove('drawer-open-lock');
            document.documentElement.style.overflow = '';
            document.body.style.overflow = '';
        });

        // Allow anchor tags inside the drawer to navigate normally
        const drawerLinks = mobileDrawer.querySelectorAll('a');
        drawerLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                // Ensure scroll locks are cleared immediately upon navigation
                document.documentElement.style.overflow = '';
                document.body.style.overflow = '';
                document.body.classList.remove('drawer-open-lock');
            });
        });
    }
});

// Newsletter subscribe (AJAX with graceful fallback)
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('newsletterForm');
    if (!form) return;
    const input = document.getElementById('newsletterEmail');
    const btn = document.getElementById('newsletterSubmitBtn');
    const msg = document.getElementById('newsletterMsg');
    const show = (text, ok) => {
        msg.textContent = text;
        msg.className = 'ft-nl-msg ' + (ok ? 'is-ok' : 'is-err');
    };
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = input.value.trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            show('Please enter a valid email address.', false);
            input.focus();
            return;
        }
        btn.disabled = true;
        const icon = btn.querySelector('i');
        icon.className = 'fas fa-spinner fa-spin';
        try {
            const res = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            const data = await res.json();
            show(data.message, data.ok);
            if (data.ok) form.reset();
        } catch (err) {
            show('Network error. Please try again.', false);
        } finally {
            btn.disabled = false;
            icon.className = 'fas fa-paper-plane';
        }
    });
});
