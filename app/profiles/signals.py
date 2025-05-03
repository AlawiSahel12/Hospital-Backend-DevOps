import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DoctorProfile, PatientProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DoctorProfile)
def update_doctor_schedules(sender, instance, **kwargs):
    """
    When a DoctorProfile is updated:
      - If the doctor is deactivated (is_active becomes False), delete all their active schedules.
    This signal is decoupled from the model and includes logging for easier maintenance.
    """
    if not instance.is_active:
        try:
            # Dynamically get the DoctorSchedule model from the schedules app.
            DoctorSchedule = apps.get_model("schedules", "DoctorSchedule")
            # Delete all active schedules for the doctor.
            deleted_count, _ = DoctorSchedule.objects.filter(
                doctor=instance.user, is_active=True
            ).delete()
            logger.info(f"Deleted {deleted_count} schedules for {instance}.")
        except Exception as e:
            logger.error(f"Error deleting doctor schedules for {instance}: {e}")


User = get_user_model()


@receiver(post_save, sender=User)
def create_patient_profile(sender, instance, created, **kwargs):
    """
    Automatically create a PatientProfile for new users with role 'patient'.
    Placed here in the profiles app to keep all profile logic centralized.
    """
    if created and instance.role == "patient":
        PatientProfile.objects.create(user=instance)
