# Generated by Django 5.1.8 on 2025-04-29 03:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('appointment', '0003_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opened_at', models.DateTimeField(blank=True, null=True)),
                ('closed_at', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.OneToOneField(limit_choices_to={'appointment_type': 'online'}, on_delete=django.db.models.deletion.CASCADE, related_name='chat_session', to='appointment.appointment')),
                ('closed_by', models.ForeignKey(blank=True, help_text='If set, the doctor manually closed the chat.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='closed_chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Chat session',
                'verbose_name_plural': 'Chat sessions',
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatsession')),
            ],
            options={
                'ordering': ['sent_at'],
            },
        ),
        migrations.AddIndex(
            model_name='chatsession',
            index=models.Index(fields=['opened_at'], name='chat_chatse_opened__6346ea_idx'),
        ),
        migrations.AddIndex(
            model_name='chatsession',
            index=models.Index(fields=['closed_at'], name='chat_chatse_closed__50cd9a_idx'),
        ),
        migrations.AddIndex(
            model_name='chatmessage',
            index=models.Index(fields=['session', 'sent_at'], name='chat_chatme_session_ab1e58_idx'),
        ),
    ]
