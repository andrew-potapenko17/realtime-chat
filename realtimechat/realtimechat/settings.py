import os
from pathlib import Path

from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent


# ── Security ───────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split()


# ── Custom user model ──────────────────────────────────────────────────────────

AUTH_USER_MODEL = "accounts.User"


# ── Applications ───────────────────────────────────────────────────────────────

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "channels",
]

LOCAL_APPS = [
    "core",
    "accounts",
    "profiles",
    "rooms",
    "chat",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ── Middleware ─────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ── URL / WSGI / ASGI ──────────────────────────────────────────────────────────

ROOT_URLCONF = "realtimechat.urls"

WSGI_APPLICATION = "realtimechat.wsgi.application"
ASGI_APPLICATION = "realtimechat.asgi.application"


# ── Templates ──────────────────────────────────────────────────────────────────
# Project-level templates/ folder + each app's own templates/ folder.

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
            ],
        },
    },
]

TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "rooms.context_processors.sidebar_rooms",
]

# ── Database ───────────────────────────────────────────────────────────────────

DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
        ),
        conn_max_age=60,
    )
}


# ── Sessions ───────────────────────────────────────────────────────────────────
# Sessions stored in the database; the cookie is HttpOnly + SameSite.
# AuthMiddlewareStack in Channels reads this same session to auth WS connections.

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14   # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG          # True in production (HTTPS only)


# ── Auth redirects ─────────────────────────────────────────────────────────────

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "rooms:lobby"
LOGOUT_REDIRECT_URL = "accounts:login"


# ── Django Channels ────────────────────────────────────────────────────────────

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (os.getenv("REDIS_HOST", "127.0.0.1"), int(os.getenv("REDIS_PORT", 6379)))
            ],
        },
    },
}


# ── Cache ──────────────────────────────────────────────────────────────────────

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": (
            f"redis://{os.getenv('REDIS_HOST', '127.0.0.1')}"
            f":{os.getenv('REDIS_PORT', 6379)}/1"
        ),
    }
}


# ── Password validation ────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ── Internationalisation ───────────────────────────────────────────────────────

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ── Static files ───────────────────────────────────────────────────────────────
# Development:  runserver serves static/ automatically when DEBUG=True.
# Production:   run collectstatic, then point Nginx at STATIC_ROOT.
#
# Layout:
#   static/          ← your source files, committed to git
#   staticfiles/     ← collectstatic output, git-ignored, served by Nginx

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ── Media files (user uploads) ─────────────────────────────────────────────────

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ── Default primary key ────────────────────────────────────────────────────────

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ── Logging ────────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django":   {"handlers": ["console"], "level": "INFO",  "propagate": False},
        "channels": {"handlers": ["console"], "level": "INFO",  "propagate": False},
        "chat":     {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}