# Generated by Django 5.1.2 on 2024-11-03 17:43

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0002_messagelog_messagetemplate_recipient_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagelog',
            options={'ordering': ['-sent_at']},
        ),
        migrations.AlterModelOptions(
            name='messagetemplate',
            options={'ordering': ['day_number']},
        ),
        migrations.AlterModelOptions(
            name='recipient',
            options={'ordering': ['-start_date']},
        ),
        migrations.RemoveField(
            model_name='messagetemplate',
            name='content',
        ),
        migrations.AddField(
            model_name='messagelog',
            name='error_message',
            field=models.TextField(blank=True, help_text='Error message if sending failed', null=True),
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='day_number',
            field=models.IntegerField(db_index=True, default=1, help_text='Day in sequence when this message should be sent', unique=True),
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='link',
            field=models.URLField(blank=True, help_text='Optional URL to be included in the message', max_length=500, null=True, validators=[django.core.validators.URLValidator()]),
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='message_text',
            field=models.TextField(default='Default message text', help_text='Message content to be sent'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='messagetemplate',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='recipient',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='recipient',
            name='current_day',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='recipient',
            name='start_date',
            field=models.DateField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipient',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_logs', to='whatsapp.recipient'),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('delivered', 'Delivered')], default='pending', max_length=20),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_logs', to='whatsapp.messagetemplate'),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='twilio_message_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='messagetemplate',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether this template is currently active'),
        ),
        migrations.AlterField(
            model_name='messagetemplate',
            name='name',
            field=models.CharField(help_text='Template name/identifier', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='recipient',
            name='phone_number',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]