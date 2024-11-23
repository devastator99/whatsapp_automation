# celery.py
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings  # Add this import

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_automation.settings')

# Initialize Celery app
app = Celery('whatsapp_automation')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Debug task (optional)
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Beat schedule configuration for daily template sending
app.conf.beat_schedule = {
    'send-scheduled-messages-every-day': {
        'task': 'whatsapp.tasks.send_daily_templates',  # Adjust to your actual app and task path
        'schedule': crontab(minute='*'),
        'options': {'timezone': 'Asia/Kolkata'}, 
    },
    # Other tasks can be added here
    #  crontab(hour=9, minute=0), 
}


# 'schedule': crontab(minute='*')  # Send scheduled messages at  every minute


# Optional task configuration
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'Asia/Kolkata'  # Set your timezone (change to your local timezone)
