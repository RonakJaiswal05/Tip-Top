import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiptop.settings.dev")

app = Celery("tiptop")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
