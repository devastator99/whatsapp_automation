from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def send_whatsapp_message(to, message):
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN

        client = Client(account_sid, auth_token)
        
        twilio_message = client.messages.create(
            body=message,
            from_="whatsapp:+919263865032", 
            to=f"whatsapp:{to}"
        )
        
        return twilio_message.sid
    
    except TwilioRestException as e:
        print(f"Twilio error: {e}")
        raise  # Re-raise the exception so it can be handled upstream

    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        raise 