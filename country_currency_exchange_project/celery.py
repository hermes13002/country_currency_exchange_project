import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'country_currency_exchange_project.settings')

app = Celery('country_currency_exchange_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()