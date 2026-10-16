# Shree Hunainath Educational Academy (श्री हुनैनाथ एजुकेसनल एकेडेमी)
> **Empowering Minds, Inspiring Futures • ज्ञान, संस्कार र उत्कृष्टता**
> Location: Shuklaphanta Municipality-5, Garjamani, Kanchanpur District, Sudurpashchim Province, Nepal

---

## 🌟 Overview & Architecture
A production-ready, dynamic **Progressive Web App (PWA)** and **School Content Management System (CMS)** designed for **Shree Hunainath Educational Academy**. Engineered to enterprise standards with Fortune-500 grade security headers, asynchronous notification broadcasting, high-performance static caching, and modern aesthetics inspired by benchmark institutions.

### 🚀 Core Capabilities
- **Full-Stack Django 5.2 Architecture:** Modular, decoupled architecture with custom in-house template rendering (no heavy frontend framework lock-in).
- **Tailwind-Powered Unfold Admin CMS:** Modern, responsive administration console with real-time KPI metrics, search, filtering, custom badges, and management workflows.
- **Progressive Web App (PWA):**
  - Offline-first caching via custom Service Worker (`sw.js`).
  - Seamless install prompt banner and native iOS Safari "Add to Home Screen" guide modal.
  - Web App Manifest (`manifest.json`) with multi-sized icons and application shortcuts.
- **Push Notification & Urgent Ticker System:**
  - VAPID-compliant Web Push notifications with subscription management.
  - Interactive breaking news marquee ticker for urgent exam schedules, holidays, and admissions.
  - Admin one-click push notification broadcaster.
- **Dynamic Multi-Environment Database Support:**
  - **Local Development:** Zero-configuration SQLite (`sqlite:///db.sqlite3`).
  - **Production:** High-concurrency PostgreSQL configured via `DATABASE_URL` (using `psycopg` v3 and `dj-database-url`).
- **Fortune-500 Enterprise Security:**
  - Content-Security-Policy (CSP) with whitelist for Google Fonts, CDNs, and Ngrok tunnels.
  - Permissions-Policy, X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), X-XSS-Protection.
  - Invisible honeypot fields on public admission and inquiry forms to neutralize spam bots.
  - Strict HTTPS session & CSRF cookie protection.
  - Branded, user-friendly 404, 500, and 403 error pages.
- **SEO & Performance Engineering:**
  - Schema.org `EducationalOrganization` JSON-LD markup on homepage and course pages.
  - OpenGraph & Twitter Card social meta tags.
  - Dynamic `sitemap.xml` and `robots.txt`.
  - Whitenoise compression and static asset cache-busting.

---

## 📂 Project Structure
```text
Hunainath Educational Academy/
├── .env                       # Environment configuration secrets & variables
├── .env.example               # Template environment file
├── .gitignore                 # Version control exclusions
├── manage.py                  # Django management CLI
├── requirements.txt           # Python dependencies
├── run_server.bat             # Server launcher script
├── run_ngrok.bat              # Ngrok tunnel launcher script
├── start_academy.bat          # Master one-click runner (Server + Ngrok)
├── db.sqlite3                 # Local SQLite database
│
├── hunainath_academy/         # Project Core Configuration
│   ├── settings.py            # Settings (Unfold, Whitenoise, Security, Dynamic DB)
│   ├── urls.py                # Root URL dispatcher & error handler mappings
│   ├── wsgi.py                # WSGI entry point for production deployment
│   └── asgi.py                # ASGI entry point for async concurrency
│
├── core/                      # Main Academy Application
│   ├── models.py              # Models: SchoolProfile, Notice, AcademicProgram, Admissions, etc.
│   ├── views.py               # Views & API endpoints (Push, Admissions, Notices, SEO)
│   ├── views_errors.py        # Custom 404, 500, 403 error handlers
│   ├── admin.py               # Unfold Admin configurations & custom display badges
│   ├── middleware.py          # Enterprise SecurityHeadersMiddleware (CSP, Permissions)
│   ├── context_processors.py  # Global context (School branding, urgent tickers)
│   ├── urls.py                # App URL routes
│   └── management/commands/
│       └── seed_data.py       # Comprehensive database seeder
│
├── static/                    # Source Static Assets
│   ├── css/
│   │   └── main.css           # Master stylesheet & design tokens
│   ├── js/
│   │   ├── main.js            # UI animations, counters, filter tabs, ripple clicks
│   │   └── pwa.js             # Service Worker, PWA install prompt, Push toggle
│   └── images/
│       ├── logo.png           # Academy logo & emblem
│       └── icons/             # Multi-sized PWA icons (72x72 to 512x512)
│
├── staticfiles/               # Whitenoise-compiled production static files
├── media/                     # Uploads (branding, notices, student photos)
└── templates/                 # In-House HTML Templates
    ├── base.html              # Base layout with navbar, footer, ticker, PWA modals
    ├── core/
    │   ├── index.html         # Homepage
    │   ├── about.html         # About Us & History
    │   ├── programs.html      # Academic programs list & filters
    │   ├── program_detail.html# Program details & subject breakdown
    │   ├── admissions.html    # Online admission registration form
    │   ├── admission_success.html # Confirmation & printable receipt
    │   ├── admission_status.html  # Application tracking portal
    │   ├── notices.html       # Official circulars & notice board
    │   ├── notice_detail.html # Circular view & attachment download
    │   ├── gallery.html       # Campus life photo gallery
    │   ├── faculty.html       # Teachers & leadership directory
    │   ├── contact.html       # Campus visit & inquiry form
    │   └── offline.html       # PWA offline fallback screen
    ├── errors/                # 404, 500, 403 branded error templates
    └── pwa/
        ├── manifest.json      # Web app manifest
        └── sw.js              # Service worker script
```

---

## 🔑 Default Credentials & Access
- **Local URL:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Ngrok Public HTTPS URL:** `https://lushly-snort-result.ngrok-free.dev`
- **Django Unfold Admin Portal:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  - **Username:** `admin`
  - **Password:** `HunainathAdmin2026!`

---

## ⚙️ Environment Configuration (`.env`)
The project utilizes a dedicated `.env` file for all environment-specific values:
```env
SECRET_KEY=hunainath-prod-sec-key-8899-7711-kanchanpur-academy-2026-!@#$x
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,.ngrok-free.app,.ngrok-free.dev,.ngrok.io,hunainath.edu.np,*

# Database: SQLite locally, PostgreSQL for production
# For production PostgreSQL: DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_URL=sqlite:///db.sqlite3

CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000,https://*.ngrok-free.app,https://*.ngrok-free.dev,https://*.ngrok.io
```

---

## 🛠️ How to Run Locally

### 1. Enable Virtual Environment & Run Django Server
Double-click `run_server.bat` or run in terminal:
```powershell
.\venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

### 2. Start Ngrok Tunnel
Double-click `run_ngrok.bat` or run:
```powershell
ngrok http 8000
```

### 3. Re-seed or Reset Sample Data (Optional)
```powershell
.\venv\Scripts\python.exe manage.py seed_data
```

---

## 🌐 Production PostgreSQL Deployment Guide
When migrating to production (e.g. AWS, Render, DigitalOcean, or Heroku):
1. Create a PostgreSQL database instance.
2. Update `.env`:
   ```env
   DEBUG=False
   DATABASE_URL=postgresql://<db_user>:<db_password>@<db_host>:5432/<db_name>
   ALLOWED_HOSTS=hunainath.edu.np,www.hunainath.edu.np
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```
3. Run migrations and collect static assets:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
4. Run using Gunicorn:
   ```bash
   gunicorn hunainath_academy.wsgi:application --bind 0.0.0.0:8000 --workers 3
   ```
#   H u n a i n a t h - E d u c a t i n a l - A c a d e m y  
 #   H u n a i n a t h - E d u c a t i n a l - A c a d e m y  
 