"""Settings shared by every environment. Secrets and anything host-specific come from environment variables.

dev.py and prod.py import from here. A local .env file (see .env.example) is read if present, but real
environment variables always win.
"""
import os
from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # .../app
REPO_DIR = BASE_DIR.parent


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in {"1", "true", "yes", "on"}


def env_list(name: str, default: str = "") -> list[str]:
    return [x.strip() for x in os.environ.get(name, default).split(",") if x.strip()]


SECRET_KEY = env("DJANGO_SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
SITE_URL = env("SITE_URL", "http://localhost:8000").rstrip("/")
ENVIRONMENT = env("ENVIRONMENT", "dev")  # dev, staging, production

INSTALLED_APPS = [
    "core.admin_config.TipTopAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    # third party
    "django_otp",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "simple_history",
    "auditlog",
    "axes",
    "anymail",
    # ours
    "core",
    "catalog",
    "shops",
    "leads",
    "content",
    "legal",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "core.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "core.middleware.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "core.middleware.StaffSessionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "core.middleware.MaintenanceMiddleware",
    "core.middleware.LegacyRedirectMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "tiptop.urls"
WSGI_APPLICATION = "tiptop.wsgi.application"

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
                "core.context_processors.site",
            ],
        },
    },
]

# ---------- Database ----------
import dj_database_url  # noqa: E402

DATABASES = {
    "default": dj_database_url.parse(
        env("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}"), conn_max_age=60, conn_health_checks=True
    )
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------- Cache (Redis in staging/production, memory locally) ----------
REDIS_URL = env("REDIS_URL", "")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
            "KEY_PREFIX": env("CACHE_PREFIX", "tt"),
            "TIMEOUT": 3600,
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "tiptop"}}

# ---------- Auth and admin security ----------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "admin:login"
LOGIN_REDIRECT_URL = "/admin/"
# Staff are signed out after STAFF_IDLE_TIMEOUT without activity (A1). Visitors never get a session.
SESSION_COOKIE_AGE = 14 * 24 * 60 * 60  # matches the cookie policy ("2 Wochen")
SESSION_SAVE_EVERY_REQUEST = False
STAFF_IDLE_TIMEOUT = 60 * 60  # seconds of inactivity before staff are signed out
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# django-axes: lock an account/IP pair after 5 failed sign-ins for 30 minutes.
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # hours
AXES_LOCKOUT_PARAMETERS = [["username", "ip_address"]]
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "admin/locked_out.html"
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = ["HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"]

OTP_TOTP_ISSUER = "TipTop Service 24"
# Roles that must sign in with a second factor (A1).
OTP_REQUIRED_GROUPS = ["Owner", "Manager"]

# ---------- Internationalisation ----------
LANGUAGE_CODE = "de"
LANGUAGES = [("de", "Deutsch"), ("en", "English")]
LANGUAGE_COOKIE_NAME = "tt-lang"
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60
LANGUAGE_COOKIE_SAMESITE = "Lax"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True

# ---------- Static and media ----------
STATIC_URL = "/static/"
STATIC_ROOT = Path(env("STATIC_ROOT", str(BASE_DIR / "staticfiles")))
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(env("MEDIA_ROOT", str(BASE_DIR / "media")))
# Files only signed-in staff may see (buyback photos). Outside MEDIA_ROOT, so Nginx never serves them.
PRIVATE_ROOT = Path(env("PRIVATE_ROOT", str(BASE_DIR / "private")))
OFFER_PHOTO_DAYS = 30  # buyback photos are deleted after this many days unless a purchase contract follows
OFFER_PHOTO_MAX = 6
OFFER_PHOTO_MAX_BYTES = 8 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000  # the price table posts one field per price

# ---------- Email ----------
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
ANYMAIL = {"BREVO_API_KEY": env("BREVO_API_KEY", "")}
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "TipTop Service 24 <info@tiptophandyreparatur.de>")
SERVER_EMAIL = env("SERVER_EMAIL", "TipTop Website <noreply@tiptophandyreparatur.de>")
EMAIL_TIMEOUT = 10

# ---------- Celery ----------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL or "memory://")
CELERY_RESULT_BACKEND = None
CELERY_TASK_IGNORE_RESULT = True
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", not bool(REDIS_URL))
CELERY_TASK_EAGER_PROPAGATES = False
CELERY_WORKER_CONCURRENCY = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 200
CELERY_TASK_ACKS_LATE = True
CELERY_BROKER_TRANSPORT_OPTIONS = {"visibility_timeout": 3600}
CELERY_BEAT_SCHEDULE = {
    "google-ratings-daily": {"task": "shops.tasks.fetch_google_ratings", "schedule": crontab(hour=5, minute=15)},
    "scheduled-prices": {"task": "catalog.tasks.apply_scheduled_prices", "schedule": crontab(minute="*")},
    "daily-summary": {"task": "leads.tasks.send_daily_summary", "schedule": crontab(hour=20, minute=45)},
    "retry-sheets": {"task": "leads.tasks.retry_unsynced", "schedule": crontab(minute="*/10")},
    "retention": {"task": "core.tasks.apply_retention", "schedule": crontab(hour=3, minute=30)},
}

# ---------- Integrations ----------
GOOGLE_PLACES_API_KEY = env("GOOGLE_PLACES_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_FILE = env("GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "secrets" / "google-service-account.json"))
SENTRY_DSN = env("SENTRY_DSN", "")

# Rate limits for public forms: requests per window per IP (and per form).
FORM_RATE_LIMIT = int(env("FORM_RATE_LIMIT", "8"))
FORM_RATE_WINDOW = int(env("FORM_RATE_WINDOW", "600"))
FORM_MIN_SECONDS = float(env("FORM_MIN_SECONDS", "2.5"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {"django.db.backends": {"level": "WARNING"}},
}

# Audit log (A12): keep 12 months, then the retention job deletes entries.
AUDITLOG_INCLUDE_ALL_MODELS = False
AUDIT_RETENTION_DAYS = 365

# Two-factor sign-in for Owner and Manager. dev.py may switch it off locally; prod.py forces it on.
OTP_ENFORCE = True
