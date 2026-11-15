from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    verbose_name = "Website und Einstellungen"

    def ready(self):
        from . import checks  # noqa: F401
        from .signals import connect_all

        connect_all()
