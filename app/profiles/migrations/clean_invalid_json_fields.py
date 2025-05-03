import json

from django.db import migrations


def clean_invalid_json_fields(apps, schema_editor):
    PatientProfile = apps.get_model("profiles", "PatientProfile")
    # Loop over all profiles to verify and clean the JSON fields
    for profile in PatientProfile.objects.all():
        # Clean allergies field
        if isinstance(profile.allergies, str):
            try:
                # Try to load the string as JSON
                json.loads(profile.allergies)
            except (ValueError, json.JSONDecodeError):
                # If not valid JSON, set to empty list
                profile.allergies = []
                profile.save(update_fields=["allergies"])

        # Clean illnesses field
        if isinstance(profile.illnesses, str):
            try:
                json.loads(profile.illnesses)
            except (ValueError, json.JSONDecodeError):
                profile.illnesses = []
                profile.save(update_fields=["illnesses"])


def reverse_func(apps, schema_editor):
    # No reverse action is needed, so just pass.
    pass


class Migration(migrations.Migration):

    dependencies = [
        # Ensure this runs after your initial migration
        ("profiles", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(clean_invalid_json_fields, reverse_func),
    ]
