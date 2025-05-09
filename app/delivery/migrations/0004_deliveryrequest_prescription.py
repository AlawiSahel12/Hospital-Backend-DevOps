# Generated by Django 5.1.8 on 2025-05-02 22:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("delivery", "0003_address"),
        ("prescriptions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliveryrequest",
            name="prescription",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="delivery_requests",
                to="prescriptions.prescriptionrecord",
            ),
            preserve_default=False,
        ),
    ]
