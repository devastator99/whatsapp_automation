from django.http import JsonResponse, HttpResponseBadRequest
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.utils import timezone
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from .services.razorpay_service import generate_payment_link
from .services.zoho_books_service import generate_invoice
from .services.twilio_service import send_whatsapp_message
from .models import Recipient, MessageTemplate, MessageLog, Quotes, Invoice
from django.conf import settings
import razorpay
import logging
import json
import time

# Import modular configuration
from .config import PlanConfig, BusinessConfig, PlanType
from .templates import MessageTemplates, TemplateManager
from .template_config import TemplateConfig



logger = logging.getLogger(__name__)
timestamp = int(time.time())

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any


class CommandType(Enum):
    """Enumeration of available command types"""
    PLAN_SELECTION = "plan_selection"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    INSPIRATION_REQUEST = "inspiration_request"
    MENU_NAVIGATION = "menu_navigation"
    UNKNOWN = "unknown"


class Command(ABC):
    """Abstract base class for all commands"""
    
    def __init__(self, recipient, message_body: str):
        self.recipient = recipient
        self.message_body = message_body
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def execute(self) -> Optional[str]:
        """Execute the command and return response message"""
        pass
    
    @abstractmethod
    def can_handle(self, message_body: str) -> bool:
        """Check if this command can handle the given message"""
        pass


class PlanSelectionCommand(Command):
    """Handle plan selection commands (1-4)"""
    
    def can_handle(self, message_body: str) -> bool:
        return message_body in ["1", "2", "3", "4"]
    
    def execute(self) -> Optional[str]:
        if not self.can_handle(self.message_body):
            return None
            
        self.recipient.selected_plan = self.message_body
        self.recipient.save()
        
        template_id = TemplateConfig.get_template_id(self.message_body)
        self.logger.info(f"Plan {self.message_body} selected by {self.recipient.phone_number}")
        
        return None  # Returns template_id via service layer


class PaymentConfirmationCommand(Command):
    """Handle payment confirmation commands (yes)"""
    
    def can_handle(self, message_body: str) -> bool:
        return message_body == "yes" and self.recipient.selected_plan is not None
    
    def execute(self) -> Optional[str]:
        if not self.can_handle(self.message_body):
            return None
            
        plan_number = self.recipient.selected_plan
        amount = PlanConfig.get_price(plan_number)
        plan_name = PlanConfig.get_name(plan_number)
        
        try:
            payment_link = generate_payment_link(amount, {
                'name': self.recipient.name,
                'email': self.recipient.email or f"{self.recipient.phone_number}@example.com",
                'contact': self.recipient.phone_number or 'numbaaa',
            })
            
            self.recipient.pending_plan = plan_name
            self.recipient.pending_amount = amount
            self.recipient.payment_status = 'pending'
            self.recipient.save()
            
            self.logger.info(f"Payment link generated for {self.recipient.phone_number}")
            return MessageTemplates.get_payment_confirmation_message(plan_name, payment_link)
            
        except Exception as e:
            self.logger.error(f"Error generating payment link: {e}")
            return MessageTemplates.get_error_message('payment_link')


class InspirationRequestCommand(Command):
    """Handle daily inspiration requests (5)"""
    
    def can_handle(self, message_body: str) -> bool:
        return message_body == "5"
    
    def execute(self) -> Optional[str]:
        if not self.can_handle(self.message_body):
            return None
            
        try:
            quote = Quotes.objects.order_by('?').first()
            message = str(quote) if quote else MessageTemplates.get_error_message('quote')
            self.logger.info(f"Inspiration quote sent to {self.recipient.phone_number}")
            return message
        except Exception as e:
            self.logger.error(f"Error fetching quote: {e}")
            return MessageTemplates.get_error_message('quote_fetch')


class MenuNavigationCommand(Command):
    """Handle menu navigation commands (menu)"""
    
    def can_handle(self, message_body: str) -> bool:
        return message_body == "menu"
    
    def execute(self) -> Optional[str]:
        if not self.can_handle(self.message_body):
            return None
            
        self.recipient.selected_plan = None
        self.recipient.save()
        
        self.logger.info(f"Menu reset for {self.recipient.phone_number}")
        return None  # Returns template_id via service layer


class UnknownCommand(Command):
    """Handle unknown commands"""
    
    def can_handle(self, message_body: str) -> bool:
        return True  # Always can handle as fallback
    
    def execute(self) -> Optional[str]:
        self.logger.info(f"Unknown command '{self.message_body}' from {self.recipient.phone_number}")
        return None  # Returns default template via service layer


class CommandFactory:
    """Factory for creating appropriate command instances"""
    
    def __init__(self):
        self.command_classes = [
            PlanSelectionCommand,
            PaymentConfirmationCommand,
            InspirationRequestCommand,
            MenuNavigationCommand,
            UnknownCommand  # Must be last
        ]
    
    def create_command(self, recipient, message_body: str) -> Command:
        """Create appropriate command based on message content"""
        for command_class in self.command_classes:
            command = command_class(recipient, message_body)
            if command.can_handle(message_body):
                return command
        
        # Fallback to UnknownCommand
        return UnknownCommand(recipient, message_body)
    
    def get_command_type(self, message_body: str) -> CommandType:
        """Get command type without creating full command instance"""
        if message_body in ["1", "2", "3", "4"]:
            return CommandType.PLAN_SELECTION
        elif message_body == "yes":
            return CommandType.PAYMENT_CONFIRMATION
        elif message_body == "5":
            return CommandType.INSPIRATION_REQUEST
        elif message_body == "menu":
            return CommandType.MENU_NAVIGATION
        else:
            return CommandType.UNKNOWN


class InputValidator:
    """Validates and sanitizes user input"""
    
    @staticmethod
    def sanitize_message(message: str) -> str:
        """Sanitize incoming message"""
        if not message:
            return ""
        return message.strip().lower()
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """Validate phone number format"""
        if not phone_number:
            return False
        
        # Remove whatsapp: prefix if present
        clean_number = phone_number.replace('whatsapp:', '')
        
        # Basic validation - should be numeric and reasonable length
        return clean_number.isdigit() and 10 <= len(clean_number) <= 15
    
    @staticmethod
    def extract_phone_number(from_field: str) -> Optional[str]:
        """Extract and validate phone number from Twilio 'From' field"""
        if not from_field:
            return None
            
        phone_number = from_field.replace('whatsapp:', '')
        
        if InputValidator.validate_phone_number(phone_number):
            return phone_number
            
        return None


class MessageTemplates:
    """Centralized message templates"""
    
    @staticmethod
    def get_welcome_message():
        return (
            f"✨ *Welcome to Your Premium Health Subscription!* 💎\n\n"
            f"Elevate your wellness journey with *exclusive access* to personalized health programs and expert guidance.\n\n"
            f"👉 Please *reply with the number* corresponding to your desired subscription tier, and we'll guide you through the next steps!\n\n"
            f"💎 *Premium Subscription Tiers:*\n\n"
            f"1️⃣ *Essential Wellness Consultation* – ₹249\n"
            f"    🍏 *Personalized nutrition strategy* and foundational health guidance.\n\n"
            f"2️⃣ *Diabetes Mastery Program* – ₹1500\n"
            f"    💉 *Advanced care protocol* for diabetes management and reversal.\n\n"
            f"3️⃣ *Body Transformation Program* – ₹1500\n"
            f"    🏋️‍♂️ *Comprehensive weight optimization* with personalized coaching.\n\n"
            f"4️⃣ *Elite Preventive Health Program* – ₹1200\n"
            f"    🩺 *Proactive health monitoring* and preventive care strategies.\n\n"
            f"5️⃣ *Daily Wellness Inspiration* ✨\n\n"
        )
    
    @staticmethod
    def get_payment_confirmation_message(plan_name, payment_link):
        return (
            f"🎉 Thank you for selecting our {plan_name}!\n"
            f"🔗 Your secure payment link: {payment_link}\n"
            f"⏳ Upon payment completion, your personal health concierge will contact you within 24 hours.\n"
            f"📜 Reply with *menu* to return to the main menu.\n"
        )
    
    @staticmethod
    def get_subscription_success_message(current_plan, invoice_url):
        return (
            f"🎉 *Payment Successful! Welcome to Your Premium Subscription!*\n\n"
            f"Thank you for your investment in wellness! Your {current_plan} is now active.\n\n"
            f"📋 Your Premium Invoice: {invoice_url}\n\n"
            f"👨‍⚕️ Your personal health concierge will contact you within 24 hours to begin your journey!\n\n"
            f"👉 Reply with *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_error_message(error_type):
        messages = {
            'payment_link': "Sorry, we couldn't generate a payment link at this time. Please try again later.",
            'quote': "Sorry, no quotes available at the moment.",
            'quote_fetch': "Sorry, we couldn't fetch a quote at this time."
        }
        return messages.get(error_type, "An error occurred. Please try again later.")


class WhatsAppService:
    """Enhanced service class for WhatsApp operations with command pattern"""
    
    def __init__(self):
        self.command_factory = CommandFactory()
        self.validator = InputValidator()
    
    @staticmethod
    def get_or_create_recipient(user_number: str):
        """Get or create recipient with default settings"""
        recipient, created = Recipient.objects.get_or_create(
            phone_number=user_number,
            defaults={
                'preferred_language': 'en',
                'is_active': False
            }
        )
        return recipient, created
    
    def process_message(self, recipient, message_body: str) -> Dict[str, Any]:
        """Process incoming message using command pattern"""
        sanitized_message = self.validator.sanitize_message(message_body)
        command = self.command_factory.create_command(recipient, sanitized_message)
        command_type = self.command_factory.get_command_type(sanitized_message)
        
        try:
            response_message = command.execute()
            
            # Handle template responses for specific commands
            template_id = None
            if command_type == CommandType.PLAN_SELECTION:
                template_id = TemplateConfig.get_plan_template(sanitized_message)
            elif command_type == CommandType.MENU_NAVIGATION:
                template_id = TemplateConfig.get_welcome_template()
            elif command_type == CommandType.UNKNOWN:
                template_id = TemplateConfig.get_welcome_template()
            
            return {
                'message': response_message,
                'template_id': template_id,
                'command_type': command_type,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing command {command_type}: {e}")
            return {
                'message': MessageTemplates.get_error_message('payment_link'),
                'template_id': None,
                'command_type': command_type,
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_message(recipient, message: Optional[str] = None, template_id: Optional[str] = None) -> str:
        """Send WhatsApp message and log it"""
        try:
            if template_id:
                message_sid = send_whatsapp_message(to=recipient.phone_number, templateid=template_id)
            elif message:
                message_sid = send_whatsapp_message(to=recipient.phone_number, message=message)
            else:
                raise ValueError("No message or template_id provided")
            
            MessageLog.objects.create(
                recipient=recipient,
                status='SENT',
                sent_at=timezone.now(),
                whatsapp_message_id=message_sid
            )
            
            return message_sid
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise
    
    def handle_webhook_request(self, request) -> Dict[str, Any]:
        """Handle webhook request with proper validation"""
        # Extract and validate phone number
        user_number = self.validator.extract_phone_number(request.POST.get('From', ''))
        if not user_number:
            return {
                'success': False,
                'error': 'Invalid or missing phone number',
                'status_code': 400
            }
        
        # Extract and validate message
        raw_message = request.POST.get('Body', '')
        if not raw_message:
            return {
                'success': False,
                'error': 'No message body provided',
                'status_code': 400
            }
        
        # Update global variable (consider removing this in future)
        global whatsapp_number
        whatsapp_number = user_number
        
        logger.info(f"Received message from {user_number}: {raw_message.strip()}")
        
        return {
            'success': True,
            'user_number': user_number,
            'message_body': raw_message.strip()
        }



def get_templateid(template_key):
    """Get template ID for given key - DEPRECATED: Use TemplateConfig.get_template_id() instead"""
    import warnings
    warnings.warn("get_templateid() is deprecated. Use TemplateConfig.get_template_id() instead.", 
                  DeprecationWarning, stacklevel=2)
    return TemplateConfig.get_template_id(template_key)


@csrf_exempt
def whatsapp_webhook(request):
    """Enhanced WhatsApp webhook with command pattern architecture"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        # Initialize service
        whatsapp_service = WhatsAppService()
        
        # Handle webhook request with validation
        webhook_result = whatsapp_service.handle_webhook_request(request)
        
        if not webhook_result['success']:
            return JsonResponse({
                'status': 'error', 
                'message': webhook_result['error']
            }, status=webhook_result['status_code'])
        
        # Get recipient
        recipient = whatsapp_service.get_or_create_recipient(webhook_result['user_number'])[0]
        
        # Process message using command pattern
        command_result = whatsapp_service.process_message(
            recipient, 
            webhook_result['message_body']
        )
        
        if not command_result['success']:
            logger.error(f"Command processing failed: {command_result.get('error')}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Command processing failed'
            }, status=500)
        
        # Send response
        whatsapp_service.send_message(
            recipient,
            command_result['message'],
            command_result['template_id']
        )
        
        logger.info(
            f"Successfully processed {command_result['command_type'].value} "
            f"command for {recipient.phone_number}"
        )
        
        return JsonResponse({
            'status': 'success',
            'command_type': command_result['command_type'].value
        })

    except Exception as e:
        logger.error(f"Critical error in whatsapp_webhook: {e}")
        return JsonResponse({
            'status': 'error', 
            'message': 'Internal server error'
        }, status=500)


class PaymentService:
    """Service class for payment processing"""
    
    @staticmethod
    def verify_webhook_signature(request):
        """Verify Razorpay webhook signature"""
        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_payment_link_id = request.GET.get('razorpay_payment_link_id')
        razorpay_payment_link_reference_id = request.GET.get('razorpay_payment_link_reference_id')
        razorpay_payment_link_status = request.GET.get('razorpay_payment_link_status')
        razorpay_signature = request.GET.get('razorpay_signature')
        
        logger.info(f"Webhook data: {razorpay_payment_id}, {razorpay_payment_link_id}, {razorpay_payment_link_status}")
        
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        
        client.utility.verify_payment_link_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_payment_link_id': razorpay_payment_link_id,
            'razorpay_payment_link_reference_id': razorpay_payment_link_reference_id,
            'razorpay_payment_link_status': razorpay_payment_link_status,
            'razorpay_signature': razorpay_signature
        })
        
        return {
            'payment_id': razorpay_payment_id,
            'payment_link_id': razorpay_payment_link_id,
            'reference_id': razorpay_payment_link_reference_id,
            'status': razorpay_payment_link_status
        }
    
    @staticmethod
    def get_payment_details(payment_id):
        """Fetch payment details from Razorpay"""
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        
        payment_details = client.payment.fetch(payment_id)
        return {
            'payment_id': payment_details['id'],
            'amount': payment_details['amount'],
            'contact': payment_details['contact']
        }
    
    @staticmethod
    def create_invoice(recipient, amount, payment_id):
        """Create invoice in Razorpay"""
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        
        invoice_data = client.invoice.create({
            "type": "invoice",
            "description": recipient.phone_number,
            "date": timestamp,
            "customer": {
                "name": "Whatsapp_user",
                "contact": recipient.phone_number,
                "billing_address": BusinessConfig.BUSINESS_ADDRESS
            },
            "sms_notify": 1,
            "currency": BusinessConfig.CURRENCY,
            "line_items": [
                {
                    "name": recipient.pending_plan,
                    "description": BusinessConfig.BUSINESS_DESCRIPTION,
                    "amount": amount,
                    "currency": BusinessConfig.CURRENCY,
                    "quantity": 1,
                }
            ],
        })
        
        return invoice_data


@csrf_exempt
def razorpay_webhook(request):
    """Handle webhook events from Razorpay"""
    logger.info("got through the razorpay-webhook!")

    try:
        webhook_data = PaymentService.verify_webhook_signature(request)
        payment_details = PaymentService.get_payment_details(webhook_data['payment_id'])
        
        logger.info(f"Payment details: {payment_details}")
        
        if not Invoice.objects.filter(payment_id=webhook_data['payment_id']).exists():
            process_successful_payment(payment_details)
            logger.info("processed SUCCESSFUL PAYMENT")

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.error(f"Error in razorpay webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class SubscriptionService:
    """Service class for subscription management"""
    
    @staticmethod
    def activate_subscription(recipient, payment_data):
        """Activate user subscription after successful payment"""
        recipient.subscription_day_number = BusinessConfig.SUBSCRIPTION_START_DAY
        recipient.is_active = True
        recipient.current_plan = recipient.pending_plan
        recipient.pending_plan = None
        recipient.pending_amount = None
        recipient.payment_status = 'paid'
        recipient.save()
    
    @staticmethod
    def create_invoice_record(recipient, payment_data, invoice_data):
        """Create invoice record in database"""
        return Invoice.objects.create(
            recipient=recipient,
            payment_id=payment_data['payment_id'],
            payment_status='paid',
            amount=int(payment_data['amount']/100),
            plan_name=recipient.pending_plan,
            invoice_id=invoice_data["id"],
            invoice_number=invoice_data["invoice_number"],
            invoice_url=invoice_data["short_url"],
        )
    
    @staticmethod
    def update_pending_message_logs(recipient):
        """Update pending message logs to paid status"""
        MessageLog.objects.filter(
            recipient=recipient,
            status='PENDING'
        ).update(status='PAID')
    
    @staticmethod
    def send_subscription_confirmation(recipient, invoice_url):
        """Send subscription confirmation message"""
        confirmation_message = MessageTemplates.get_subscription_success_message(
            recipient.current_plan, invoice_url
        )
        
        message_sid = send_whatsapp_message(to=recipient.phone_number, message=confirmation_message)
        
        MessageLog.objects.create(
            recipient=recipient,
            status='SENT',
            sent_at=timezone.now(),
            whatsapp_message_id=message_sid
        )
        
        return message_sid


def process_successful_payment(payment_data):
    """Process successful payment, generate invoice, and activate subscription"""
    try:
        payment_id = payment_data.get('payment_id')
        amount = payment_data.get('amount')
        contact = payment_data.get('contact')
        number1 = whatsapp_number

        logger.info(f"Processing payment: {payment_id}, {amount}, {contact}, {number1}")

        # Find recipient
        try:
            recipient = Recipient.objects.get(phone_number=number1)
        except Recipient.DoesNotExist:
            logger.error(f"No recipient found for contact: {contact}")
            raise ValueError(f"No recipient found for contact: {contact}")

        # Check if payment was already processed
        if Invoice.objects.filter(payment_id=payment_id).exists():
            logger.info(f"Payment {payment_id} was already processed")
            return

        # Create invoice
        invoice_data = PaymentService.create_invoice(recipient, amount, payment_id)
        invoice_url = invoice_data['short_url']
        
        logger.info(f"Invoice created: {invoice_data}")

        # Create invoice record
        SubscriptionService.create_invoice_record(recipient, payment_data, invoice_data)

        # Activate subscription
        SubscriptionService.activate_subscription(recipient, payment_data)

        # Update pending message logs
        SubscriptionService.update_pending_message_logs(recipient)

        # Send confirmation
        SubscriptionService.send_subscription_confirmation(recipient, invoice_url)

        logger.info(f"Successfully processed payment {payment_id} for recipient {recipient.phone_number}")
        return Invoice.objects.get(payment_id=payment_id)

    except Exception as e:
        logger.error(f"Error processing payment: {e}")
        raise


def payment_success(request):
    """Display payment success page"""
    return HttpResponse("""
        <html>
            <body style="text-align: center; padding: 50px;">
                <h1>Payment Successful!</h1>
                <p>You can close this window and return to WhatsApp.</p>
            </body>
        </html>
    """)


def payment_failure(request):
    """Display payment failure page"""
    return HttpResponse("""
        <html>
            <body style="text-align: center; padding: 50px;">
                <h1>Payment Failed</h1>
                <p>Please try again or contact support.</p>
            </body>
        </html>
    """)


def home(request):
    """Home page endpoint"""
    return HttpResponse(f"Welcome to {BusinessConfig.BUSINESS_NAME}!")
