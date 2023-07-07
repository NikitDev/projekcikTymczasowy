from django.apps import AppConfig


class licznik_czasuConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'licznik_czasu'

    def ready(self):
        from . import signals