from django.apps import AppConfig


class licznik_czasuConfig(AppConfig):
    name = 'licznik_czasu'

    def ready(self):
        from . import signals  # noqa:F401
        from . import tasks  # noqa:F401
