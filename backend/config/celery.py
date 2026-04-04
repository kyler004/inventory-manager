import os
from celery import Celery

# Tell celery which django setting to use
# Will change later when ready for prod
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develpment')


app = Celery('inventory')

# Read Celery config from Django settings (the CELERY_* variables)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in every installed app
# This means any tasks.py file we create in our apps/ folder
# will be automatically registered
app.autodiscover_tasks()