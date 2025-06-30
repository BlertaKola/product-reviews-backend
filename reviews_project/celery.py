import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reviews_project.settings")

app = Celery("reviews_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
