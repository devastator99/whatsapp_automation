from django.contrib import admin
from django.urls import path
from whatsapp import views
from whatsapp.scheduled_messages import schedule_messages



urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
    path('send-message/', views.send_manual_message, name='send-manual-message'),
    path('automatic',schedule_messages , name="schedule_messages"),
]