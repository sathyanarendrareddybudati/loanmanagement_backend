from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loanmanagement_backend.settings')

app = Celery('loanmanagement_backend')


app.conf.update(timezone = 'Asia/kolkata')
app.config_from_object(settings)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')