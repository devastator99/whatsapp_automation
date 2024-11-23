import requests
import logging
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_invoice(recipient, payment_id, payment_status, amount, plan_name):
    """
    Generate an invoice in Zoho for the completed payment.
    
    Args:
        recipient (Recipient): The Recipient object associated with the payment.
        payment_id (str): The Razorpay payment ID.
        payment_status (str): The status of the payment (e.g., 'paid', 'failed').
        amount (int): The amount paid, in paise.
        plan_name (str): The name of the subscribed plan.
    
    Returns:
        dict: The invoice details, including the invoice ID.
    
    Raises:
        ValueError: If required parameters are missing or invalid.
        ZohoAPIError: If there's an issue with the Zoho API call.
    """
    # Input validation
    if not all([recipient.name, recipient.email, payment_id, amount, plan_name]):
        raise ValueError("Missing required information")
    
    try:
        zoho_api_url = settings.ZOHO_API_URL
        zoho_access_token = settings.ZOHO_ACCESS_TOKEN
        
        # Prepare the invoice data
        invoice_data = {
            "customerName": recipient.name,
            "customerEmail": recipient.email,
            "customerPhone": recipient.phone_number,
            "customerNote": f"Razorpay Payment ID: {payment_id}",
            "items": [
                {
                    "name": plan_name,
                    "description": f"{plan_name} - {payment_status}",
                    "quantity": 1,
                    "rate": amount / 100,
                }
            ],
            "paymentOption": {
                "enable": True,
                "paymentLink": ""
                # f"{settings.SITE_URL}/payment"
            },
            "templateId": settings.ZOHO_INVOICE_TEMPLATE_ID,
            "status": "draft"
        }
        
        headers = {
            "Authorization": f"Zoho-oauthtoken {zoho_access_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Attempting to create invoice for {recipient.name}")
        
        response = requests.post(zoho_api_url, json=invoice_data, headers=headers)
        
        if response.status_code == 200:
            logger.info("Invoice created successfully")
            return {
                "invoice_id": response.json()["invoice_id"],
                "invoice_number": response.json()["invoice_number"],
                "invoice_url": response.json().get('invoice_url')
            }
        else:
            error_message = response.text
            logger.error(f"Failed to create invoice. Status code: {response.status_code}. Error message: {error_message}")
            raise ZohoAPIError(error_message)

    except ValueError as ve:
        logger.error(f"Invalid input: {ve}")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error occurred: {e}")
        raise ZohoAPIError(str(e))
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise ZohoAPIError(str(e))

class ZohoAPIError(Exception):
    """Custom exception for Zoho API errors."""
    pass
