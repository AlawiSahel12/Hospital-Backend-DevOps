# Generated by Django 5.1.8 on 2025-05-01 21:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0004_alter_json_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalLeaveRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_file', models.URLField()),
                ('from_date', models.DateField()),
                ('to_date', models.DateField()),
                ('exams_included', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_leave_records', to='profiles.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_leave_records', to='profiles.patientprofile')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
