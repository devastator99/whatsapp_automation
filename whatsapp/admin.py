
from django.contrib import admin
from .models import Recipient, MessageTemplate, MessageLog, Quotes , Invoice

admin.site.register(Recipient)
admin.site.register(MessageTemplate)
admin.site.register(MessageLog)
admin.site.register(Quotes)
admin.site.register(Invoice)
