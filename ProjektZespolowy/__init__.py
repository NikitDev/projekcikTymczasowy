import os

from celery import app as celery_app, Celery

__all__ = ('celery_app',)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjektZespolowy.settings')

app = Celery('ProjektZespolowy')
app.config_from_object('django.conf:settings', namespace='CELERY')
