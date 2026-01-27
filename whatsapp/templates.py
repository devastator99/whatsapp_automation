"""
Message templates for the WhatsApp Health Subscription Service
"""
from typing import Dict, Optional
from .config import PlanConfig, BusinessConfig


class MessageTemplates:
    """Centralized message templates with dynamic content generation"""
    
    @staticmethod
    def get_welcome_message() -> str:
        """Generate welcome message with all available plans"""
        plans = PlanConfig.get_all_plans()
        
        message = (
            f"✨ *Welcome to Your {BusinessConfig.BUSINESS_NAME}!* 💎\\n\\n"
            f"Elevate your wellness journey with *exclusive access* to personalized health programs and expert guidance.\\n\\n"
            f"👉 Please *reply with the number* corresponding to your desired subscription tier, and we'll guide you through the next steps!\\n\\n"
            f"💎 *Premium Subscription Tiers:*\\n\\n"
        )
        
        # Add each plan to the message
        for plan_id, plan_details in plans.items():
            plan_number = plan_id
            plan_name = plan_details['name']
            plan_price = plan_details['price']
            plan_description = plan_details['description']
            
            message += f"{plan_number}️⃣ *{plan_name}* – ₹{plan_price}\\n"
            message += f"    {plan_description}\\n\\n"
        
        # Add inspiration option
        message += f"5️⃣ *Daily Wellness Inspiration* ✨\\n\\n"
        
        return message
    
    @staticmethod
    def get_plan_info_message(plan_id: str) -> str:
        """Generate detailed information for a specific plan"""
        plan_name = PlanConfig.get_name(plan_id)
        plan_price = PlanConfig.get_price(plan_id)
        plan_description = PlanConfig.get_description(plan_id)
        
        return (
            f"📋 *{plan_name}*\\n\\n"
            f"💰 **Price:** ₹{plan_price}\\n"
            f"📝 **Details:** {plan_description}\\n\\n"
            f"👉 Reply with *yes* to proceed with payment, or *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_payment_confirmation_message(plan_name: str, payment_link: str) -> str:
        """Generate payment confirmation message"""
        return (
            f"🎉 Thank you for selecting our {plan_name}!\\n"
            f"🔗 Your secure payment link: {payment_link}\\n"
            f"⏳ Upon payment completion, your personal health concierge will contact you within {BusinessConfig.PAYMENT_TIMEOUT_MINUTES} minutes.\\n"
            f"📜 Reply with *menu* to return to the main menu.\\n"
        )
    
    @staticmethod
    def get_subscription_success_message(current_plan: str, invoice_url: str) -> str:
        """Generate subscription activation success message"""
        return (
            f"🎉 *Payment Successful! Welcome to Your Premium Subscription!*\\n\\n"
            f"Thank you for your investment in wellness! Your {current_plan} is now active.\\n\\n"
            f"📋 Your Premium Invoice: {invoice_url}\\n\\n"
            f"👨‍⚕️ Your personal health concierge will contact you within 24 hours to begin your journey!\\n\\n"
            f"👉 Reply with *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_payment_failure_message() -> str:
        """Generate payment failure message"""
        return (
            f"❌ *Payment Failed*\\n\\n"
            f"We're sorry, but your payment could not be processed.\\n\\n"
            f"🔹 Please check your payment details and try again\\n"
            f"🔹 Contact support at {BusinessConfig.SUPPORT_EMAIL} if the issue persists\\n\\n"
            f"👉 Reply with *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_quote_message(quote_text: str) -> str:
        """Generate daily inspiration quote message"""
        return (
            f"💫 *Daily Wellness Inspiration*\\n\\n"
            f"\"{quote_text}\"\\n\\n"
            f"🌟 Remember: Your health journey is unique and beautiful!\\n\\n"
            f"👉 Reply with *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_error_message(error_type: str) -> str:
        """Generate error messages based on error type"""
        error_messages = {
            'payment_link': "Sorry, we couldn't generate a payment link at this time. Please try again later.",
            'quote': BusinessConfig.QUOTE_FALLBACK_MESSAGE,
            'quote_fetch': "Sorry, we couldn't fetch a quote at this time.",
            'invalid_plan': "Invalid plan selection. Please choose a valid plan number.",
            'payment_processing': "Error processing payment. Please contact support.",
            'general': "An error occurred. Please try again later.",
            'recipient_not_found': "User account not found. Please restart the conversation.",
            'server_error': "Server error. Our team has been notified. Please try again later."
        }
        
        base_message = error_messages.get(error_type, error_messages['general'])
        
        return (
            f"❌ *Oops! Something went wrong*\\n\\n"
            f"{base_message}\\n\\n"
            f"📞 Need help? Contact us at {BusinessConfig.SUPPORT_EMAIL}\\n\\n"
            f"👉 Reply with *menu* to return to the main menu."
        )
    
    @staticmethod
    def get_menu_reset_message() -> str:
        """Generate menu reset confirmation message"""
        return (
            f"🔄 *Menu Reset*\\n\\n"
            f"Welcome back to the main menu!\\n\\n"
            f"💎 Choose your premium health subscription:\\n"
            f"1️⃣ Essential Wellness - ₹249\\n"
            f"2️⃣ Diabetes Mastery - ₹1500\\n"
            f"3️⃣ Body Transformation - ₹1500\\n"
            f"4️⃣ Elite Preventive - ₹1200\\n"
            f"5️⃣ Daily Inspiration\\n\\n"
            f"👉 Reply with a number to get started!"
        )
    
    @staticmethod
    def get_subscription_expiry_message(days_left: int) -> str:
        """Generate subscription expiry reminder message"""
        return (
            f"⏰ *Subscription Reminder*\\n\\n"
            f"Your premium subscription will expire in {days_left} day{'s' if days_left != 1 else ''}.\\n\\n"
            f"🔗 Reply with *renew* to continue your wellness journey\\n"
            f"📞 Contact support at {BusinessConfig.SUPPORT_EMAIL} for assistance\\n\\n"
            f"Thank you for trusting us with your health! 🌟"
        )
    
    @staticmethod
    def get_support_message() -> str:
        """Generate customer support information message"""
        return (
            f"🤝 *Customer Support*\\n\\n"
            f"We're here to help you on your wellness journey!\\n\\n"
            f"📧 **Email:** {BusinessConfig.SUPPORT_EMAIL}\\n"
            f"📞 **Phone:** {BusinessConfig.SUPPORT_PHONE}\\n"
            f"🏢 **Address:** {BusinessConfig.BUSINESS_ADDRESS['line1']}\\n"
            f"   {BusinessConfig.BUSINESS_ADDRESS['line2']}\\n"
            f"   {BusinessConfig.BUSINESS_ADDRESS['city']}, {BusinessConfig.BUSINESS_ADDRESS['state']} {BusinessConfig.BUSINESS_ADDRESS['zipcode']}\\n\\n"
            f"👉 Reply with *menu* to return to the main menu."
        )


class TemplateManager:
    """Manager class for template operations"""
    
    @staticmethod
    def get_template_by_context(context: str, **kwargs) -> str:
        """Get template based on context and parameters"""
        context_map = {
            'welcome': MessageTemplates.get_welcome_message,
            'plan_info': lambda: MessageTemplates.get_plan_info_message(kwargs.get('plan_id', '')),
            'payment_confirmation': lambda: MessageTemplates.get_payment_confirmation_message(
                kwargs.get('plan_name', ''), kwargs.get('payment_link', '')
            ),
            'subscription_success': lambda: MessageTemplates.get_subscription_success_message(
                kwargs.get('current_plan', ''), kwargs.get('invoice_url', '')
            ),
            'payment_failure': MessageTemplates.get_payment_failure_message,
            'quote': lambda: MessageTemplates.get_quote_message(kwargs.get('quote_text', '')),
            'error': lambda: MessageTemplates.get_error_message(kwargs.get('error_type', 'general')),
            'menu_reset': MessageTemplates.get_menu_reset_message,
            'subscription_expiry': lambda: MessageTemplates.get_subscription_expiry_message(
                kwargs.get('days_left', 0)
            ),
            'support': MessageTemplates.get_support_message,
        }
        
        template_func = context_map.get(context)
        if template_func:
            return template_func()
        
        return MessageTemplates.get_error_message('general')
