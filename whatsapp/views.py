# views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Recipient, MessageTemplate
from .tasks import send_whatsapp_message
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Get credentials from settings, not hardcoded
client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def get_response_for_message(message):
    """
    Returns appropriate response based on user message
    """
    message = message.lower().strip()
    
    responses = {
        'hi': "Welcome to our service! How can I help you today?",
        'hello': "Hello there! What can I do for you?",
        'bye': "Goodbye! Have a great day!",
        'help': """
        I can help you with:
        1. Information about our services
        2. Technical support
        3. Booking appointments
        4. General inquiries
        
        Just type what you need!
        """.strip(),
    }
    
    return responses.get(message, "I'm not sure how to respond to that. Type 'help' for available options.")

@csrf_exempt
def webhook(request):
    """
    Handles incoming WhatsApp messages
    """
    if request.method != "POST":
        return HttpResponse("This endpoint only accepts POST requests.", status=405)
    
    try:
        print(request)
        # Get the incoming message details
        incoming_msg = request.POST.get('Body', '').lower()
        sender_number = request.POST.get('From', '')
        
        if not sender_number:
            logger.error("No sender number provided")
            return HttpResponse("Sender number is required", status=400)
        
        # Remove 'whatsapp:' prefix if present
        sender_number = sender_number.replace('whatsapp:', '')
        
        # Create a TwiML response
        resp = MessagingResponse()
        
        # Get or create recipient
        recipient, created = Recipient.objects.get_or_create(
            phone_number=sender_number,
            defaults={'name': f'User-{sender_number[-4:]}'}  # Last 4 digits as temp name
        )
        
        # Get appropriate response
        response_text = get_response_for_message(incoming_msg)
        
        # Get default template
        try:
            template = MessageTemplate.objects.get(name="Default Response")
        except ObjectDoesNotExist:
            template = MessageTemplate.objects.create(
                name="Default Response",
                content=response_text
            )
        
        # Send response using Celery task
        send_whatsapp_message.delay(
            recipient_id=recipient.id,
            template_id=template.id
        )
        
        # Log success
        logger.info(f"Successfully processed message from {sender_number}")
        return HttpResponse(str(resp))
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing webhook: {str(e)}")
        
        # Create error response
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again later.")
        
        return HttpResponse(str(resp), status=500)

# Optional: Additional endpoints for manual message sending
def send_manual_message(request):
    """
    Example endpoint for manually sending messages
    """
    if request.method != "POST":
        return HttpResponse("This endpoint only accepts POST requests.", status=405)
    
    try:
        recipient_id = request.POST.get('recipient_id')
        template_id = request.POST.get('template_id')
        
        if not all([recipient_id, template_id]):
            return HttpResponse("recipient_id and template_id are required", status=400)
        
        # Schedule message sending
        send_whatsapp_message.delay(
            recipient_id=recipient_id,
            template_id=template_id
        )
        
        return HttpResponse("Message scheduled successfully")
        
    except Exception as e:
        logger.error(f"Error scheduling message: {str(e)}")
        return HttpResponse("Error scheduling message", status=500)