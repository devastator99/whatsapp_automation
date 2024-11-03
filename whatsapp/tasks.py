# tasks.py
from twilio.rest import Client
from django.conf import settings
from .models import MessageLog, Recipient, MessageTemplate
from celery import shared_task

@shared_task
def send_whatsapp_message(recipient_id, template_id):
    """
    Celery task to send WhatsApp message
    """
    try:
        # Initialize Twilio client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Get recipient and template objects
        recipient = Recipient.objects.get(id=recipient_id)
        template = MessageTemplate.objects.get(id=template_id)
        
        # Send message
        message = client.messages.create(
            from_=f'whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}',
            body=template.content,
            to=f'whatsapp:{recipient.phone_number}'
        )
        
        # Log successful message
        MessageLog.objects.create(
            recipient=recipient,
            template=template,
            status='SENT',
            twilio_message_id=message.sid
        )
        
        return {
            'success': True,
            'message_sid': message.sid,
            'recipient': recipient.name,
            'phone': recipient.phone_number
        }
        
    except Recipient.DoesNotExist:
        return {
            'success': False,
            'error': f'Recipient with id {recipient_id} not found'
        }
        
    except MessageTemplate.DoesNotExist:
        return {
            'success': False,
            'error': f'Template with id {template_id} not found'
        }
        
    except Exception as e:
        # Log failed message
        MessageLog.objects.create(
            recipient_id=recipient_id,
            template_id=template_id,
            status='FAILED'
        )
        
        return {
            'success': False,
            'error': str(e)
        }

# Example usage of how to schedule messages
@shared_task
def schedule_messages():
    """
    Task to schedule messages for multiple recipients
    """
    recipients = Recipient.objects.filter(is_active=True)
    template = MessageTemplate.objects.get(name="Inactive Template")  # or whatever template you want to use
    
    for recipient in recipients:
        # Schedule message to be sent
        send_whatsapp_message.delay(recipient.id, template.id)