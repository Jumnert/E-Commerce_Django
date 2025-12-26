import os
from pathlib import Path

# ------------------------
# Base directory
# ------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------
# Secret key & debug
# ------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-local-fallback-key")

DEBUG = os.environ.get("DEBUG", "True") == "True"  # True locally, False on Render

# ------------------------
# Allowed hosts
# ------------------------
# Works both locally and on Render
ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,e-commerce-django-b47w.onrender.com"
).split(",")

ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS if host.strip()]

CSRF_TRUSTED_ORIGINS = [
    "https://e-commerce-django-b47w.onrender.com",
]


# ------------------------
# Installed apps
# ------------------------
INSTALLED_APPS = [
    'django_daisy',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "store",
    "django_extensions",
]

DAISY_THEME = "dracula"


UNFOLD = {
    "SITE_TITLE": "E-Commerce Admin",
    "SITE_HEADER": "E-Commerce Dashboard",
    "THEME": "light",  # light / dark / auto
}

# ------------------------
# Middleware
# ------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # must be after SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------
# URL configuration
# ------------------------
ROOT_URLCONF = "jewelryshop.urls"
WSGI_APPLICATION = "jewelryshop.wsgi.application"

# ------------------------
# Templates
# ------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "store.context_preprocessors.store_menu",
                "store.context_preprocessors.cart_menu",
            ],
        },
    },
]

# ------------------------
# Database (SQLite for demo)
# ------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ------------------------
# Password validation
# ------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ------------------------
# Internationalization
# ------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ------------------------
# Static files (CSS, JS)
# ------------------------
STATIC_URL = "/static/"

# Folder for development static files
STATICFILES_DIRS = [BASE_DIR / "jewelryshop" / "static"]

# Folder for production static files (WhiteNoise serves this)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------
# Media files (uploads)
# ------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------
# Default primary key field type
# ------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------
# Email backend
# ------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ------------------------
# Security for proxy headers (Render)
# ------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
