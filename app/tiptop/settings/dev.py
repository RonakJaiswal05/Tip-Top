"""Local development: SQLite unless DATABASE_URL is set, console email, Celery tasks run inline."""
from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-only-insecure-key-change-me")
ALLOWED_HOSTS = ["*"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
# Two-factor sign-in can be switched off locally for convenience; it is always on in staging and production.
OTP_ENFORCE = env("OTP_ENFORCE", "0") == "1"
