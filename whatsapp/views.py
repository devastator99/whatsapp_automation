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



logger = logging.getLogger(__name__)
timestamp = int(time.time())


def get_welcome_message():
    return (
        f"👋 *Welcome to ANUBHOOTI HEALTH!🧘‍♂️* \n\n"
        f"We are here to help you achieve your health goals with *personalized care* and expert guidance.\n\n"
        f"👉 Please *reply with the number* corresponding to the plan you're interested in, and we'll guide you through the next steps!\n\n"
        f"💡 *Our Plans:*\n\n"
        f"1️⃣ *General Dietary Consultation* – ₹249\n"
        f"    🍏 *Personalized advice* on nutrition and healthy eating habits.\n\n"
        f"2️⃣     *Diabetes Reversal & Care Program* – ₹1500\n"
        f"    💉 A *comprehensive plan* to help manage and reverse diabetes.\n\n"
        f"3️⃣     *Weight Management & Care Program* – ₹1500\n"
        f"    🏋️‍♂️ Tailored support for *achieving and maintaining your ideal weight*.\n\n"
        f"4️⃣     *Preventive Health Program* – ₹1200\n"
        f"    🩺 Focus on *early detection and prevention* of health risks.\n\n"
        f"5️⃣ *Get Inspired!* ✨\n\n"
    )


# Constants for plan details
PLAN_PRICES = {
    "1": 249,  # General Dietary Consultation
    "2": 1500,  # Diabetes Reversal
    "3": 1500,  # Weight Management
    "4": 1200,  # Preventive Health
}

PLAN_NAMES = {
    "1": "General Dietary Consultation",
    "2": "Diabetes Reversal & Care Program",
    "3": "Weight Management & Care Program",
    "4": "Preventive Health Program",
}


def get_templateid(template_key):
    template_mapping = {
        "1" : "HX401909eb770b3582fc1b93f816f0f737",  # PLAN INFO 1
        "2" : "HX6c6f2b8a3de9c3fbf9752d06796c374f",  # PLAN INFO 2
        "3" : "HXbba16f9b75de2d1c46ec7096a22e594c",
        "4" : "HXdbbe90b4d4e7be2809d6cb1a63cb83f3",
        "5" : "HXfa57cb7d295f8e43447d82f41b11d976",  #WELCOME MESSAGE 
    }
    
    if template_key not in template_mapping:
        logger.error(f"invalid template key : {template_key}")
        return template_mapping.get("5")
    
    return template_mapping.get(template_key)



@csrf_exempt
def whatsapp_webhook(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid request method')

    try:
        user_number = request.POST.get('From', '').replace('whatsapp:', '')
        message_body = request.POST.get('Body', '').strip().lower()
        global whatsapp_number
        whatsapp_number = user_number

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN

        logger.info(f"Received message from {user_number}: {message_body}")

        if not user_number:
            return JsonResponse({'status': 'error', 'message': 'No phone number provided'}, status=400)

        message=None
        templateid=None

        # Get or create recipient with default language
        recipient, created = Recipient.objects.get_or_create(
            phone_number=user_number,
            defaults={
                'preferred_language': 'en',
                'is_active': False
            }
        )

        # Handle user input
        if message_body in ["1", "2", "3", "4"]:
            # Store the selected plan in the recipient model
            recipient.selected_plan = message_body
            recipient.save()
            # message = get_plan_info(message_body)
            templateid = get_templateid(message_body)

        elif message_body == "yes" and recipient.selected_plan:
            plan_number = recipient.selected_plan
            amount = PLAN_PRICES[plan_number]
            plan_name = PLAN_NAMES[plan_number]

            try:

                logger.info(f"generated p link rev")
                payment_link = generate_payment_link(amount, {
                    'name': recipient.name,
                    'email': recipient.email or f"{user_number}@example.com",
                    'contact': recipient.phone_number or 'numbaaa',
                })

                logger.info(f"generated p link")

                # Store pending plan details
                recipient.pending_plan = plan_name
                recipient.pending_amount = amount
                recipient.payment_status = 'pending'
                recipient.save()

                logger.info(f"model update success!!!")

                message = (
                    f"🎉 Thank you for choosing our {plan_name}!\n"
                    f"🔗 Here's your payment link: {payment_link}\n"
                    f"⏳ After completing the payment, our health expert will contact you within 24 hours.\n"
                    f"📜 Reply with *menu* to return to the main menu.\n"
                )

            except Exception as e:
                logger.error(f"Error generating payment link: {e}")
                message = "Sorry, we couldn't generate a payment link at this time. Please try again later."

        elif message_body == "5":
            try:
                quote = Quotes.objects.order_by('?').first()
                message = str(
                    quote) if quote else "Sorry, no quotes available at the moment."
            except Exception as e:
                logger.error(f"Error fetching quote: {e}")
                message = "Sorry, we couldn't fetch a quote at this time."

        elif message_body == "menu":
            # Clear the selected plan
            recipient.selected_plan = None
            recipient.save()
            templateid = get_templateid("5") 

        else:
            templateid = get_templateid("5")
            # Sending a template message
            # message_sid = send_whatsapp_message(to=recipient.phone_number,templateid="HX219fc6a91ce4b76621f1d87f90bbf1fb")

        

        # Send WhatsApp message
        try:
            if templateid:
                message_sid = send_whatsapp_message(to=recipient.phone_number,templateid=templateid)
            elif message:
                message_sid = send_whatsapp_message(to=recipient.phone_number, message = message)
            else:
                raise ValueError("No message var and no templateid var available!!!")
            # Log the message
            MessageLog.objects.create(
                recipient=recipient,
                status='SENT',
                sent_at=timezone.now(),
                whatsapp_message_id=message_sid
            )

            logger.info("SUCCESSFULLY SKIMMED THROUGH WHATSAPP-WEBHOOK")

            return JsonResponse({'status': 'success'})

        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    except Exception as e:
        logger.error(f"Unexpected error in whatsapp_webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def razorpay_webhook(request):
    """Handle webhook events from Razorpay"""
    # if request.method != 'POST':
    #     return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

    logger.info("got through the razorpay-webhook!")

    try:
        # Verify webhook signature
        # webhook_signature = request.headers.get('X-Razorpay-Signature')
        # webhook_body = request.body.decode('utf-8')
        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_payment_link_id = request.GET.get('razorpay_payment_link_id')
        razorpay_payment_link_reference_id = request.GET.get(
            'razorpay_payment_link_reference_id')
        razorpay_payment_link_status = request.GET.get(
            'razorpay_payment_link_status')
        razorpay_signature = request.GET.get('razorpay_signature')

        logger.info(razorpay_payment_id)
        logger.info(razorpay_payment_link_id)
        logger.info(razorpay_payment_link_reference_id)
        logger.info(razorpay_payment_link_status)
        logger.info(razorpay_signature)

        logger.info("fetched webhook signature in rzp")

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
        # client.utility.verify_webhook_signature(
        #     webhook_body,
        #     webhook_signature,
        #     settings.RAZORPAY_WEBHOOK_SECRET,
        # )

        client.utility.verify_payment_link_signature({
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_payment_link_id': razorpay_payment_link_id,
            'razorpay_payment_link_reference_id': razorpay_payment_link_reference_id,
            'razorpay_payment_link_status': razorpay_payment_link_status,
            'razorpay_signature': razorpay_signature
        })

        logger.info('---verified---')

        payment_details1 = client.payment.fetch(razorpay_payment_id)
        contact = payment_details1['contact']
        amount = payment_details1['amount']

        logger.info(payment_details1)

        payment_data = {
            "payment_id": razorpay_payment_id,
            "amount": amount,
            "contact": contact,
        }

        # You can now access the values like this:
        logger.info(payment_data)

        logger.info('--------------------')
        # logger.info(webhook_body)
        logger.info('ABOVE IS THE WEBHOOK BODY')

        logger.info("initialized the rzp client")
        # payload = json.loads(webhook_body)
        # payment_data = payload.get('payload', {}).get(
        #     'payment', {}).get('entity', {})

        logger.info('--------------------')
        # logger.info(payload)
        logger.info('ABOVE IS THE PAYLOAD!!!')

        # logger.info(payment_data)
        logger.info("got payment data !!!----!!!")
        # logger.info(payload)

        # if payload.get('event') == 'payment.captured':
        #     logger.info("checking for payment.captured")
        #     # Check if payment was already processed (to avoid duplicate processing)
        #     payment_id = payment_data.get('id')
        #     logger.info("got payment data")
        #     logger.info(payment_id)
        if not Invoice.objects.filter(payment_id=razorpay_payment_id).exists():
            process_successful_payment(payment_data)
            logger.info("processed SUCCESSFUL PAYMENT")

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.error(f"Error in razorpay webhook: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def process_successful_payment(payment_data):
    """
    Process successful payment, generate invoice, and update models
    """
    try:
        payment_id = payment_data.get('payment_id')
        amount = payment_data.get('amount')  # Amount in rupees
        contact = payment_data.get('contact')
        number1 = whatsapp_number

        logger.info(payment_id)
        logger.info(amount)
        logger.info(contact)
        logger.info('THESE ARE THE REQUESTS INSIDE process_successful_payment')
        logger.info(number1)

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

        logger.info('reached the zoho breakpoint')

        client2 = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        logger.info('initialized the client')

        logger.info("-----TIMESTAMP-------")
        logger.info(timestamp)
        logger.info("------------------------")
        logger.info(recipient.name)
        name1 = recipient.name

        invoice_data = client2.invoice.create({
            "type": "invoice",
            "description": contact,
            "date": timestamp,
            "customer": {
                "name": "Whatsapp_user",
                "contact": contact,
                "billing_address": {
                    "line1": "NC 9, near Gayatri Mandir Road, Housing Board Colony,\n",
                    "line2": "East Indira Nagar, Kankarbagh, Lohia Nagar, Patna, Bihar",
                    "zipcode": "800020",
                    "city": "Patna",
                    "state": "Bihar",
                    "country": "in"
                }
            },
            "sms_notify": 1,
            "currency": "INR",
                        "line_items": [
                            {
                                "name": recipient.pending_plan,
                                "description": "anubhooti health",
                                "amount": amount,
                                "currency": "INR",
                                "quantity": 1,
                            }
            ],
        })

        logger.info("-----INVOICE_DATA-------")
        logger.info(invoice_data)
        logger.info("------------------------")

        url = invoice_data['short_url']

        logger.info("--------------2----------")
        logger.info(url)
        logger.info("------------4------------")
        # Create invoice record
        invoice = Invoice.objects.create(
            recipient=recipient,
            payment_id=payment_id,
            payment_status='paid',
            amount=int(amount/100),
            plan_name=recipient.pending_plan,
            invoice_id=invoice_data["id"],
            invoice_number=invoice_data["invoice_number"],
            invoice_url=invoice_data["short_url"],
        )

        logger.info("-----------6-------------")

        # Update recipient status
        recipient.subscription_day_number = 1
        recipient.is_active = True
        recipient.current_plan = recipient.pending_plan
        recipient.pending_plan = None
        recipient.pending_amount = None
        recipient.payment_status = 'paid'
        recipient.save()

        logger.info("--------------7----------")
        # Update any pending message logs
        MessageLog.objects.filter(
            recipient=recipient,
            status='PENDING'
        ).update(status='PAID')

        logger.info("---------------8---------")
        # Send confirmation message via WhatsApp
        confirmation_message = (
            f"🎉 *Payment Successful!*\n\n"
            f"Thank you for your payment! Your {recipient.current_plan} has been activated.\n\n"
            f"📋 Invoice: {url}\n\n"
            f"👨‍⚕️ Our health expert will contact you within 24 hours to get started!\n\n"
            f"👉 Reply with *menu* to return to the main menu."
        )

        logger.info("-----------9-------------")

        message_sid = send_whatsapp_message(to = recipient.phone_number,message= confirmation_message)

        logger.info("------------10------------")

        # Log confirmation message
        MessageLog.objects.create(
            recipient=recipient,
            status='SENT',
            sent_at=timezone.now(),
            whatsapp_message_id=message_sid
        )

        logger.info("----------11--------------")

        logger.info(
            f"Successfully processed payment {payment_id} for recipient {recipient.phone_number}")
        return invoice

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
    return HttpResponse("Welcome to the Anubhooti Health!")
