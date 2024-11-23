
import razorpay
from django.conf import settings
from django.http import JsonResponse
import logging


logger = logging.getLogger(__name__)
# payment_link = generate_payment_link(1500, {"name": recipient.name, "email": "user@example.com"})


def generate_payment_link(amount, user_details):
    try:

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))

        logger.info("reached over here 1")
        payment = client.payment_link.create({
            "amount": amount * 100,
            "currency": "INR",
            "description": "Diabetes Reversal Plan",
            "customer": {"name": user_details['name'],
                         "email": user_details['email'],
                         "contact": user_details['contact'] },
            "notify": {
                "sms": True,
                "email": True,
            },
            "reminder_enable": True,
            "callback_url": settings.PAYMENT_CALLBACK_URL,
            "callback_method": "get",
        })

        logger.info("reached over here 2")

        return payment['short_url']

    except razorpay.errors.GatewayError as e:
        print(f"Razorpay error GatewayError:  {e}")
        raise  # Re-raise the error to be handled by the caller

    except razorpay.errors.ServerError as e:
        print(f"Razorpay error ServerError: {e}")
        raise  # Re-raise the error to be handled by the caller

    except razorpay.errors.SignatureVerificationError as e:
        print(f"Razorpay error  SignatureVerificationError: {e}")
        raise  # Re-raise the error to be handled by the caller

    except razorpay.errors.BadRequestError as e:
        print(f"Razorpay error BadRequestError: {e}")
        raise  # Re-raise the error to be handled by the caller

    except Exception as e:
        print(f"Error generating payment link: {e}")
        raise  # Re-raise the error to be handled by the caller
