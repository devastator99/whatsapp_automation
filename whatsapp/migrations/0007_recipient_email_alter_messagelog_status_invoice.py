# Generated by Django 5.1.2 on 2024-11-11 19:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0006_messagetemplate_link_alter_quotes_quote'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipient',
            name='email',
            field=models.EmailField(blank=True, help_text="Recipient's email address", max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('SENT', 'Sent'), ('DELIVERED', 'Delivered'), ('FAILED', 'Failed'), ('READ', 'Read'), ('PAID', 'Paid')], default='PENDING', max_length=10),
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(help_text='Razorpay payment ID', max_length=100)),
                ('payment_status', models.CharField(help_text="Payment status (e.g., 'paid', 'failed')", max_length=20)),
                ('amount', models.PositiveIntegerField(help_text='Amount paid, in paise')),
                ('plan_name', models.CharField(help_text='Name of the subscribed plan', max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('invoice_id', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_number', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_url', models.URLField(blank=True, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='whatsapp.recipient')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['payment_id'], name='whatsapp_in_payment_a149d5_idx'), models.Index(fields=['payment_status'], name='whatsapp_in_payment_d74aac_idx'), models.Index(fields=['created_at'], name='whatsapp_in_created_ebf2a2_idx')],
            },
        ),
    ]