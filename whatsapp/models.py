from django.db import models
from django.core.validators import URLValidator
from django.utils import timezone

class Recipient(models.Model):
    """
    Represents message recipients with their subscription status and progress
    """
    name = models.CharField(max_length=100)
    phone_number = models.CharField(
        max_length=20, 
        unique=True,  # Ensures no duplicate phone numbers
    )
    start_date = models.DateField()  # When the message sequence starts
    current_day = models.IntegerField(
        default=1,  # Tracks which day's message should be sent next
    )
    is_active = models.BooleanField(
        default=True,  # Controls whether recipient should receive messages
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']  # Orders recipients by start date

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def advance_day(self):
        """Advance the current day counter"""
        self.current_day += 1
        self.save()


class MessageTemplate(models.Model):
    """
    Stores message templates for different days in the sequence
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Template name/identifier"
    )
    day_number = models.IntegerField(
        # unique=True,  # Ensures only one template per day
        help_text="Day in sequence when this message should be sent",
        db_index=True,  # Improves query performance
        default=1  
    )
    message_text = models.TextField(
        help_text="Message content to be sent"
    )
    link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        blank=True,
        null=True,
        help_text="Optional URL to be included in the message"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is currently active"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_number']  # Orders templates by day number

    def __str__(self):
        return f"Day {self.day_number}: {self.name}"

    def get_full_message(self):
        """Returns the complete message with link if present"""
        if self.link:
            return f"{self.message_text}\n\n{self.link}"
        return self.message_text


class MessageLog(models.Model):
    """
    Logs all message sending attempts and their outcomes
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered')
    ]

    recipient = models.ForeignKey(
        Recipient, 
        on_delete=models.CASCADE,
        related_name='message_logs'
    )
    template = models.ForeignKey(
        MessageTemplate, 
        on_delete=models.CASCADE,
        related_name='message_logs'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    twilio_message_id = models.CharField(
        max_length=100, 
        null=True,
        blank=True
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if sending failed"
    )

    class Meta:
        ordering = ['-sent_at']  # Most recent messages first

    def __str__(self):
        return f"{self.recipient.name} - {self.sent_at}"