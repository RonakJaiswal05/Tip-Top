"""Local performance check only (Lighthouse): production-like static files and gzip without Nginx.

    DJANGO_SETTINGS_MODULE=tiptop.settings.perf python manage.py collectstatic --noinput
    DJANGO_SETTINGS_MODULE=tiptop.settings.perf python manage.py runserver 127.0.0.1:8002 --insecure
"""
from .dev import *  # noqa: F401,F403
from .dev import BASE_DIR, MIDDLEWARE

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
STATIC_ROOT = BASE_DIR / "staticfiles-perf"
MIDDLEWARE = ["django.middleware.gzip.GZipMiddleware", MIDDLEWARE[0], "whitenoise.middleware.WhiteNoiseMiddleware"] + MIDDLEWARE[1:]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
WHITENOISE_MAX_AGE = 31536000
SERVE_MEDIA = True
