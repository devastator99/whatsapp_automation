from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging
import json

logger = logging.getLogger(__name__)

def send_whatsapp_message(to, message=None, templateid=None, content_variables=None):
    try:
        # Fetch Twilio credentials from Django settings
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN

        logger.info(f"Twilio Account SID: {account_sid}")

        # Initialize Twilio client
        client = Client(account_sid, auth_token)

        # Prepare the message payload
        if templateid:
            # Use template-based message
            message_payload = {
                "content_sid": templateid,  # Template ID
                "from_": "whatsapp:+919263865032",  # Twilio WhatsApp sender
                "to": f"whatsapp:{to}",  # Recipient
            }

            # Add content variables if provided
            if content_variables:
                message_payload["content_variables"] = json.dumps(content_variables)

        else:
            # Use plain-text message
            if not message:
                raise ValueError("Message body is required when templateid is not provided.")
            
            message_payload = {
                "body": message,  # Message text
                "from_": "whatsapp:+919263865032",  # Twilio WhatsApp sender
                "to": f"whatsapp:{to}",  # Recipient
            }

        # Send the message using Twilio
        twilio_message = client.messages.create(**message_payload)

        # Log and return message SID
        logger.info(f"Message sent successfully. SID: {twilio_message.sid}")
        return twilio_message.sid

    except TwilioRestException as e:
        logger.error(f"Twilio error: {e}")
        raise  # Re-raise Twilio-specific exceptions for upstream handling

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        raise  # Re-raise general exceptions

