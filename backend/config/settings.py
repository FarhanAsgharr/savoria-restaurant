"""
Django settings for the Savoria restaurant project.

Configuration is driven entirely by environment variables (12-factor style)
via `django-environ`, so the same codebase runs unchanged in development
(SQLite) and production (PostgreSQL on Render / Railway).
"""

from pathlib import Path

import environ

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
# BASE_DIR = .../backend  (the directory that contains manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────
# Environment
# ─────────────────────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000", "http://127.0.0.1:3000"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SECURE_SSL_REDIRECT=(bool, False),
)

# Read the .env file if present (development). In production the platform
# injects real environment variables and this file simply won't exist.
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# ─────────────────────────────────────────────────────────────
# Core security
# ─────────────────────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-only-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ─────────────────────────────────────────────────────────────
# Applications
# ─────────────────────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "menu",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise serves static files in production without a separate CDN.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CorsMiddleware must sit as high as possible, before CommonMiddleware.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ─────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────
# If DATABASE_URL is provided (production / Render / Railway) we use it,
# otherwise we fall back to a local SQLite file for development.
if env("DATABASE_URL", default=None):
    DATABASES = {
        "default": env.db("DATABASE_URL"),
    }
    # Keep connections alive for performance on managed Postgres.
    DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ─────────────────────────────────────────────────────────────
# Password validation
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─────────────────────────────────────────────────────────────
# Internationalization
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("TIME_ZONE", default="UTC")
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# Static & media files
# ─────────────────────────────────────────────────────────────
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────────────────────────────────────
# Django REST Framework
# ─────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        # Browsable API kept only in development for convenience.
        *(
            ["rest_framework.renderers.BrowsableAPIRenderer"]
            if DEBUG
            else []
        ),
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("ANON_THROTTLE_RATE", default="120/min"),
    },
}

# ─────────────────────────────────────────────────────────────
# CORS — only the trusted frontend origins may call the API
# ─────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# ─────────────────────────────────────────────────────────────
# Frontend & email
# ─────────────────────────────────────────────────────────────
# Public URL of the customer-facing site. Used by the Admin "VIEW SITE" link.
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

# Email backend for admin password-reset messages.
# Dev: print emails to the console. Prod: configure SMTP via env vars.
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="Savoria <no-reply@savoria.local>"
)

# ─────────────────────────────────────────────────────────────
# Production hardening (only active when DEBUG is False)
# ─────────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "menu": {
            "handlers": ["console"],
            "level": env("APP_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
    },
}
