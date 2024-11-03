
from django.contrib import admin
from .models import Recipient, MessageTemplate, MessageLog

admin.site.register(Recipient)
admin.site.register(MessageTemplate)
admin.site.register(MessageLog)
