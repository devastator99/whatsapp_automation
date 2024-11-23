# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Recipient, MessageTemplate, MessageLog
from .services.twilio_service import send_whatsapp_message
import logging

logger = logging.getLogger(__name__) 

@shared_task
def send_daily_templates():
    today = timezone.now().day
    recipients = Recipient.objects.filter(is_active=True)  

    for recipient in recipients:
        try:

            if recipient.subscription_day_number >= 18:
                # Set the is_active flag to False and skip sending the message
                recipient.is_active = False
                recipient.save()
                logger.info(f"Recipient {recipient.phone_number} has completed the subscription. Set is_active to False.")
                continue 
            # Fetch the template for today's scheduled message
            template = MessageTemplate.objects.filter(day_number=recipient.subscription_day_number, is_active=True).first()
            
            if template:
                
                message = template.get_template_for_language(recipient.preferred_language)

                if template.link:
                    message += f"\n\nCheck this out: {template.link}"

                logger.info(f"Sending message to {recipient.phone_number}: {message}")
                
                message_sid = send_whatsapp_message(recipient.phone_number, message)
                logger.info(f"Message sent successfully to {recipient.phone_number}, Message SID: {message_sid}")
                
                # Log
                MessageLog.objects.create(
                    recipient=recipient,
                    template=template,
                    status='SENT',
                    sent_at=timezone.now(),
                    whatsapp_message_id=message_sid
                )

                recipient.subscription_day_number += 1
                recipient.save()

                logger.info(f"SCHEDULED TASK SENT : CELERY")
                
                logger.info(f"Message sent to {recipient.phone_number}, Message SID: {message_sid}")
            else:
                # Log 
                logger.warning(f"No active template found for day {today}. Skipping recipient {recipient.phone_number}.")
        
        except Exception as e:
            # Log 
            logger.error(f"Failed to send message to {recipient.phone_number}: {e}")
            MessageLog.objects.create(
                recipient=recipient,
                template=template if 'template' in locals() else None,
                status='FAILED',
                error_message=str(e),
                sent_at=timezone.now()
            )
