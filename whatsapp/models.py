from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
    ]

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        help_text="WhatsApp number with country code (e.g., +911234567890)"
    )
    name = models.CharField(
        max_length=100,
        default='New_User',
        help_text="Recipient's full name",
        blank=True
    )
    preferred_language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        help_text="Preferred language for communication"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the recipient is active and should receive messages"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    subscription_day_number = models.IntegerField(
        default=1,
        help_text="Day number when the user subscribed and will increment after every message."
    )
    email = models.EmailField(
        null=True,
        blank=True,
        help_text="Recipient's email address"
    )
    pending_plan = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Plan selected but not yet paid for"
    )
    pending_amount = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Amount pending for selected plan"
    )
    current_plan = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Currently active plan"
    )
    payment_status = models.CharField(
        max_length=20,
        default='pending',
        help_text="Status of latest payment"
    )
    selected_plan = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class MessageTemplate(models.Model):
    day_number = models.IntegerField(
        help_text="Day number when this message should be sent",
        default=1
    )
    name = models.CharField(
        max_length=100,
        help_text="Template name for identification"
    )
    link = models.URLField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Optional URL to send along with the template message"
    )
    english_template = models.TextField(
        help_text="Message template in English. Use {name} for recipient name."
    )
    hindi_template = models.TextField(
        help_text="Message template in Hindi. Use {name} for recipient name."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is currently in use"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['day_number']),
            models.Index(fields=['is_active']),
        ]
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.name}"

    def get_template_for_language(self, language):
        return self.english_template if language == 'en' else self.hindi_template


class MessageLog(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('READ', 'Read'),
        ('PAID', 'Paid'),
    ]

    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name='message_logs'
    )
    template = models.ForeignKey(
        MessageTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='message_logs'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True
    )
    error_message = models.TextField(
        null=True,
        blank=True
    )
    whatsapp_message_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Twilio message ID for tracking"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['sent_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        recipient_name = self.recipient.name if self.recipient else "Unknown Recipient"
        template_name = self.template.name if self.template else "No Template"
        return f"{recipient_name} - {template_name} ({self.status})"


class Invoice(models.Model):
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    payment_id = models.CharField(
        max_length=100,
        help_text="Razorpay payment ID"
    )
    payment_status = models.CharField(
        max_length=20,
        help_text="Payment status (e.g., 'paid', 'failed')"
    )
    amount = models.PositiveIntegerField(
        help_text="Amount paid, in paise"
    )
    plan_name = models.CharField(
        max_length=100,
        help_text="Name of the subscribed plan"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    invoice_id = models.CharField(max_length=100, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_url = models.URLField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.phone_number} - {self.plan_name} ({self.payment_status})"



class Quotes(models.Model):
    quote = models.TextField(
        help_text="Quotes from swami vivekananda"
    )

    class Meta:
        indexes = [
            models.Index(fields=['quote']),
        ]

    def __str__(self):
        return f"{self.quote}"
