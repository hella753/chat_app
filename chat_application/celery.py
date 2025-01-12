from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_application.settings')

import django
django.setup()

app = Celery('chat_application')

app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Tbilisi')

app.config_from_object(settings, namespace='CELERY')

app.autodiscover_tasks()