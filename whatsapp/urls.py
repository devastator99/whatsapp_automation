
from django.urls import path
from . import views

urlpatterns = [
    path('whatsapp-webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    path('razorpay-webhook/', views.razorpay_webhook, name='razorpay_webhook'),
    path('payment-failure/', views.payment_failure, name='payment-failure'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('', views.home, name='home'),
]
