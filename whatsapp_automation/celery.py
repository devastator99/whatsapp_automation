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
app.autodiscover_tasks()

# Debug task (optional)
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Beat schedule configuration
app.conf.beat_schedule = {
    'send-scheduled-messages': {
        'task': 'whatsapp.tasks.schedule_messages',  # Change this to your actual app and task name
        'schedule': crontab(minute='*/1'), 
    },
    # You can add more scheduled tasks here
}

# Optional task configuration
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
app.conf.timezone = 'UTC'  # Set your timezone