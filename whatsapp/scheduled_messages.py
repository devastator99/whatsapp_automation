# scheduled_messages.py

from django.conf import settings
from celery import shared_task
from .models import Recipient, MessageTemplate
from .tasks import send_whatsapp_message

@shared_task
def schedule_messages():
    try:
        # Fetch recipients and templates
        recipients = Recipient.objects.filter(is_active=True)
        templates = MessageTemplate.objects.filter(is_active=True)

        # Process each recipient-template pair
        for recipient in recipients:
            for template in templates:
                send_whatsapp_message().send_message.delay(recipient.phone_number, template)

        print("All scheduled messages processed successfully.")
    except Exception as e:
        print(f"An error occurred while scheduling messages: {str(e)}")
