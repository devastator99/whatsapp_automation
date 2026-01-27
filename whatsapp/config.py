"""
Configuration constants for the WhatsApp Health Subscription Service
"""
from enum import Enum
from typing import Dict


class PlanType(Enum):
    """Enumeration of available health plans"""
    ESSENTIAL_WELLNESS = "1"
    DIABETES_MASTERY = "2"
    BODY_TRANSFORMATION = "3"
    ELITE_PREVENTIVE = "4"


class PlanConfig:
    """Configuration for health plans"""
    
    # Plan pricing in INR
    PRICES: Dict[str, int] = {
        PlanType.ESSENTIAL_WELLNESS.value: 249,
        PlanType.DIABETES_MASTERY.value: 1500,
        PlanType.BODY_TRANSFORMATION.value: 1500,
        PlanType.ELITE_PREVENTIVE.value: 1200,
    }
    
    # Plan display names
    NAMES: Dict[str, str] = {
        PlanType.ESSENTIAL_WELLNESS.value: "Essential Wellness Consultation",
        PlanType.DIABETES_MASTERY.value: "Diabetes Mastery Program",
        PlanType.BODY_TRANSFORMATION.value: "Body Transformation Program",
        PlanType.ELITE_PREVENTIVE.value: "Elite Preventive Health Program",
    }
    
    # Plan descriptions for welcome message
    DESCRIPTIONS: Dict[str, str] = {
        PlanType.ESSENTIAL_WELLNESS.value: "🍏 *Personalized nutrition strategy* and foundational health guidance.",
        PlanType.DIABETES_MASTERY.value: "💉 *Advanced care protocol* for diabetes management and reversal.",
        PlanType.BODY_TRANSFORMATION.value: "🏋️‍♂️ *Comprehensive weight optimization* with personalized coaching.",
        PlanType.ELITE_PREVENTIVE.value: "🩺 *Proactive health monitoring* and preventive care strategies.",
    }
    
    @classmethod
    def get_price(cls, plan_id: str) -> int:
        """Get price for a specific plan"""
        return cls.PRICES.get(plan_id, 0)
    
    @classmethod
    def get_name(cls, plan_id: str) -> str:
        """Get name for a specific plan"""
        return cls.NAMES.get(plan_id, "Unknown Plan")
    
    @classmethod
    def get_description(cls, plan_id: str) -> str:
        """Get description for a specific plan"""
        return cls.DESCRIPTIONS.get(plan_id, "Plan description not available")
    
    @classmethod
    def get_all_plans(cls) -> Dict[str, Dict[str, str]]:
        """Get all plans with their details"""
        return {
            plan_id: {
                'name': cls.get_name(plan_id),
                'price': cls.get_price(plan_id),
                'description': cls.get_description(plan_id)
            }
            for plan_id in cls.PRICES.keys()
        }


class BusinessConfig:
    """Business-related configuration constants"""
    
    # Business information
    BUSINESS_NAME = "Premium Health Subscription Service"
    BUSINESS_DESCRIPTION = "Premium Health Subscription"
    
    # Contact information
    SUPPORT_EMAIL = "support@healthsubscription.com"
    SUPPORT_PHONE = "+91XXXXXXXXXX"
    
    # Business address for invoices
    BUSINESS_ADDRESS = {
        "line1": "NC 9, near Gayatri Mandir Road, Housing Board Colony,",
        "line2": "East Indira Nagar, Kankarbagh, Lohia Nagar, Patna, Bihar",
        "zipcode": "800020",
        "city": "Patna",
        "state": "Bihar",
        "country": "in"
    }
    
    # Subscription settings
    TRIAL_DAYS = 0
    SUBSCRIPTION_START_DAY = 1
    
    # Payment settings
    CURRENCY = "INR"
    PAYMENT_TIMEOUT_MINUTES = 30
    
    # Message settings
    MAX_MESSAGE_LENGTH = 1600
    QUOTE_FALLBACK_MESSAGE = "Sorry, no quotes available at the moment."
