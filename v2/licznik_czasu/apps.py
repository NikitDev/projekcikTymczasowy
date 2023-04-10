from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class licznik_czasuConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'licznik_czasu'

    def ready(self):
        from . import signals