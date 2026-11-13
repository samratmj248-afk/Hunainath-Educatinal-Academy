"""
Django settings for Shree Hunainath Educational Academy project.
Fortune-500 Enterprise Security & Performance Architecture.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url
from django.urls import reverse_lazy

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# ------------------------------------------------------------------------------
# CORE SECURITY & ENVIRONMENT
# ------------------------------------------------------------------------------
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-hunainath-academy-super-secure-key-2026-production-xyz",
)

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Allowed Hosts with support for comma-separated env values and ngrok wildcards
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]
if "*" not in ALLOWED_HOSTS and DEBUG:
    ALLOWED_HOSTS.append("*")

# CSRF Trusted Origins for Cloudflare, Ngrok and custom domains
_env_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _env_csrf.split(",")
    if origin.strip()
]

# Ensure Cloudflare and tunnel origins are always trusted
_always_trusted = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://*.trycloudflare.com",
    "https://needed-budgets-winds-recognition.trycloudflare.com",
    "https://*.ngrok-free.app",
    "https://*.ngrok-free.dev",
    "https://*.ngrok.io",
    "https://*.ngrok.app",
]
for _t in _always_trusted:
    if _t not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_t)


# ------------------------------------------------------------------------------
# APPLICATION DEFINITION
# Note: 'unfold' must precede 'django.contrib.admin'
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # Local apps
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "hunainath_academy.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.school_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "hunainath_academy.wsgi.application"
ASGI_APPLICATION = "hunainath_academy.asgi.application"

# ------------------------------------------------------------------------------
# DATABASE CONFIGURATION (Dynamic: SQLite Local, Postgres Production)
# ------------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ------------------------------------------------------------------------------
# PASSWORD VALIDATION
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ------------------------------------------------------------------------------
# INTERNATIONALIZATION & LOCALIZATION
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kathmandu"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# STATIC & MEDIA FILES
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Whitenoise configuration for optimal caching & performance
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------------------
# FORTUNE-500 ENTERPRISE SECURITY
# ------------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "strict-origin-when-cross-origin"

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 86400 * 7  # 7 days

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() in ("true", "1")
    CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True").lower() in ("true", "1")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ------------------------------------------------------------------------------
# DJANGO UNFOLD THEME CMS CONFIGURATION
# ------------------------------------------------------------------------------
UNFOLD = {
    "SITE_TITLE": "Hunainath Academy Management System",
    "SITE_HEADER": "Welcome to Hunainath Management System",
    "SITE_SUBHEADER": "Administration & Operations Portal",
    "SITE_URL": "/",
    "SITE_SYMBOL": "school",
    "SITE_LOGO": {
        "light": lambda request: "/static/images/logo.png",
        "dark": lambda request: "/static/images/logo.png",
    },
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "DASHBOARD_CALLBACK": "core.views.dashboard_callback",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Dashboard",
                "separator": False,
                "collapsible": False,
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": lambda request: reverse_lazy("admin:index"),
                    },
                    {
                        "title": "Live Website",
                        "icon": "open_in_new",
                        "link": lambda request: "/",
                    },
                    {
                        "title": "App QR & A4 Standee",
                        "icon": "qr_code_2",
                        "link": lambda request: reverse_lazy("admin_qr_standee"),
                    },
                ],
            },
            {
                "title": "Content Management",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Notices & Circulars",
                        "icon": "campaign",
                        "link": lambda request: reverse_lazy("admin:core_notice_changelist"),
                    },
                    {
                        "title": "Blog & Articles",
                        "icon": "article",
                        "link": lambda request: reverse_lazy("admin:core_blogpost_changelist"),
                    },
                    {
                        "title": "Gallery Photos",
                        "icon": "photo_library",
                        "link": lambda request: reverse_lazy("admin:core_galleryitem_changelist"),
                    },
                    {
                        "title": "Testimonials",
                        "icon": "star",
                        "link": lambda request: reverse_lazy("admin:core_testimonial_changelist"),
                    },
                ],
            },
            {
                "title": "School",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "School Profile",
                        "icon": "account_balance",
                        "link": lambda request: reverse_lazy("admin:core_schoolprofile_changelist"),
                    },
                    {
                        "title": "Academic Programs",
                        "icon": "auto_stories",
                        "link": lambda request: reverse_lazy("admin:core_academicprogram_changelist"),
                    },
                    {
                        "title": "Admission Applications",
                        "icon": "how_to_reg",
                        "link": lambda request: reverse_lazy("admin:core_admissionapplication_changelist"),
                    },
                    {
                        "title": "Teachers & Staff",
                        "icon": "badge",
                        "link": lambda request: reverse_lazy("admin:core_facultymember_changelist"),
                    },
                ],
            },
            {
                "title": "Exams & Results",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Exam Routines",
                        "icon": "event_note",
                        "link": lambda request: reverse_lazy("admin:core_examroutine_changelist"),
                    },
                    {
                        "title": "Exam Results",
                        "icon": "analytics",
                        "link": lambda request: reverse_lazy("admin:core_examresult_changelist"),
                    },
                ],
            },
            {
                "title": "Engagement",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Inquiries & Messages",
                        "icon": "mark_email_unread",
                        "link": lambda request: reverse_lazy("admin:core_contactinquiry_changelist"),
                    },
                    {
                        "title": "Newsletter Issues",
                        "icon": "forward_to_inbox",
                        "link": lambda request: reverse_lazy("admin:core_newsletter_changelist"),
                    },
                    {
                        "title": "Newsletter Subscribers",
                        "icon": "group_add",
                        "link": lambda request: reverse_lazy("admin:core_newslettersubscriber_changelist"),
                    },
                    {
                        "title": "Web Push Subscribers",
                        "icon": "notifications_active",
                        "link": lambda request: reverse_lazy("admin:core_pushsubscription_changelist"),
                    },
                    {
                        "title": "Broadcast Notifications",
                        "icon": "send",
                        "link": lambda request: reverse_lazy("admin:core_broadcastnotification_changelist"),
                    },
                ],
            },
            {
                "title": "Settings",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "User Accounts",
                        "icon": "person",
                        "link": lambda request: reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "User Groups & Roles",
                        "icon": "groups",
                        "link": lambda request: reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}

# ------------------------------------------------------------------------------
# WEB PUSH & VAPID CREDENTIALS
# ------------------------------------------------------------------------------
VAPID_PUBLIC_KEY = os.getenv(
    "VAPID_PUBLIC_KEY",
    "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U",
)
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "AVN_VAPID_PRIVATE_KEY_SECURE_TOKEN_2026")
VAPID_CLAIMS_SUB = os.getenv("VAPID_CLAIMS_SUB", "mailto:admin@hunainath.edu.np")

# ------------------------------------------------------------------------------
# EMAIL (Newsletter delivery)
# Default: console backend (emails printed in terminal). Set EMAIL_HOST etc. in .env for real SMTP.
# ------------------------------------------------------------------------------
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend" if EMAIL_HOST else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", f"Hunainath Educational Academy <{EMAIL_HOST_USER or 'no-reply@hunainath.edu.np'}>"
)


