"""
Template ID mappings for WhatsApp message templates
"""
from typing import Dict


class TemplateConfig:
    """Configuration for WhatsApp template IDs"""
    
    # Template ID mappings
    TEMPLATE_IDS: Dict[str, str] = {
        "1": "HX401909eb770b3582fc1b93f816f0f737",  # PLAN INFO 1
        "2": "HX6c6f2b8a3de9c3fbf9752d06796c374f",  # PLAN INFO 2
        "3": "HXbba16f9b75de2d1c46ec7096a22e594c",  # PLAN INFO 3
        "4": "HXdbbe90b4d4e7be2809d6cb1a63cb83f3",  # PLAN INFO 4
        "5": "HXfa57cb7d295f8e43447d82f41b11d976",  # WELCOME MESSAGE
        "payment_success": "HX_payment_success_template_id",  # Payment success template
        "payment_failure": "HX_payment_failure_template_id",  # Payment failure template
        "subscription_reminder": "HX_subscription_reminder_template_id",  # Subscription reminder
        "support": "HX_support_template_id",  # Support information template
    }
    
    # Template categories
    PLAN_TEMPLATES = ["1", "2", "3", "4"]
    NAVIGATION_TEMPLATES = ["5"]
    TRANSACTION_TEMPLATES = ["payment_success", "payment_failure"]
    NOTIFICATION_TEMPLATES = ["subscription_reminder", "support"]
    
    @classmethod
    def get_template_id(cls, template_key: str) -> str:
        """Get template ID for given key with fallback"""
        template_id = cls.TEMPLATE_IDS.get(template_key)
        
        if not template_id:
            # Log error and return default template
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Invalid template key: {template_key}")
            return cls.TEMPLATE_IDS.get("5")  # Fallback to welcome template
        
        return template_id
    
    @classmethod
    def get_plan_template(cls, plan_id: str) -> str:
        """Get template ID for a specific plan"""
        return cls.get_template_id(plan_id)
    
    @classmethod
    def get_welcome_template(cls) -> str:
        """Get welcome message template ID"""
        return cls.get_template_id("5")
    
    @classmethod
    def get_transaction_template(cls, transaction_type: str) -> str:
        """Get transaction-related template ID"""
        return cls.get_template_id(f"payment_{transaction_type}")
    
    @classmethod
    def get_notification_template(cls, notification_type: str) -> str:
        """Get notification template ID"""
        return cls.get_template_id(notification_type)
    
    @classmethod
    def validate_template_key(cls, template_key: str) -> bool:
        """Check if template key exists"""
        return template_key in cls.TEMPLATE_IDS
    
    @classmethod
    def get_all_templates(cls) -> Dict[str, str]:
        """Get all template mappings"""
        return cls.TEMPLATE_IDS.copy()
