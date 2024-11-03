from django.core.management.base import BaseCommand
from ...models import Recipient, MessageTemplate, MessageLog
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Clear existing data (optional)
        Recipient.objects.all().delete()
        MessageTemplate.objects.all().delete()
        MessageLog.objects.all().delete()

        # Create Recipients
        recipients = [
            Recipient(name="John Doe", phone_number="+1234567890"),
            Recipient(name="Jane Smith", phone_number="+917870650300"),
            Recipient(name="Mike Johnson", phone_number="+15551234567"),
            Recipient(name="Emily Brown", phone_number="+19998887777"),
            Recipient(name="David Wilson", phone_number="+16665554444", is_active=False)
        ]
        Recipient.objects.bulk_create(recipients)

        # Create Message Templates
        templates = [
            MessageTemplate(
                name="Welcome Message", 
                content="Welcome to our service! We're glad you're here."
            ),
            MessageTemplate(
                name="Appointment Reminder", 
                content="Reminder: You have an upcoming appointment tomorrow."
            ),
            MessageTemplate(
                name="Birthday Wishes", 
                content="Happy Birthday! Wishing you a fantastic day!"
            ),
            MessageTemplate(
                name="Inactive Template", 
                content="This is an inactive template.", 
                is_active=False
            )
        ]
        MessageTemplate.objects.bulk_create(templates)

        # Create Message Logs
        # First, fetch the created objects
        all_recipients = Recipient.objects.all()
        all_templates = MessageTemplate.objects.filter(is_active=True)

        message_logs = []
        import random

        # Create some sample message logs
        for recipient in all_recipients:
            for _ in range(random.randint(1, 3)):  # Each recipient gets 1-3 message logs
                template = random.choice(all_templates)
                message_logs.append(
                    MessageLog(
                        recipient=recipient,
                        template=template,
                        status=random.choice(['sent', 'delivered', 'failed']),
                        twilio_message_id=f"TW{random.randint(10000, 99999)}"
                    )
                )

        MessageLog.objects.bulk_create(message_logs)

        # Output results
        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
