"""Staging and production. Everything secret or host-specific comes from the environment (see deploy/env.example)."""
from .base import *  # noqa: F401,F403
from .base import ENVIRONMENT, SENTRY_DSN, env, env_bool, env_list

DEBUG = False
if not SECRET_KEY:  # noqa: F405
    raise RuntimeError("DJANGO_SECRET_KEY must be set")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
OTP_ENFORCE = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
LANGUAGE_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(env("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False  # mail and other services on subdomains are not ours to force
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"
USE_X_FORWARDED_HOST = False

if env("EMAIL_BACKEND") is None and env("BREVO_API_KEY"):
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"

LOGGING["handlers"]["file"] = {  # noqa: F405
    "class": "logging.handlers.WatchedFileHandler",
    "filename": env("LOG_FILE", "/var/log/tiptop/app.log"),
    "formatter": "plain",
}
LOGGING["root"]["handlers"] = ["console", "file"]  # noqa: F405

if SENTRY_DSN:
    import sentry_sdk

    # Use an EU-region DSN (e.g. a *.de.sentry.io project). No personal data is sent.
    sentry_sdk.init(dsn=SENTRY_DSN, environment=ENVIRONMENT, send_default_pii=False, traces_sample_rate=0.0)
