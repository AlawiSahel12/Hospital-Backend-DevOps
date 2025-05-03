from django.conf import settings
from django.db import models


class AbstractProfile(models.Model):
    """
    Abstract base model for profile types.
    Contains common fields like timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PatientProfile(AbstractProfile):
    """
    Patient-specific profile extending the common User model.
    Automatically linked to a user upon creation.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_profile",  # explicitly set for consistency
    )
    blood_type = models.CharField(max_length=3, blank=True)
    allergies = models.JSONField(blank=True, null=True, default=list)
    illnesses = models.JSONField(blank=True, null=True, default=list)

    def __str__(self):
        return self.user.get_full_name()


class DoctorProfile(AbstractProfile):
    """
    Extends the common User model for doctor-specific attributes.
    The related_name is explicitly set to "doctor_profile" to keep compatibility with other parts of the app.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",  # explicitly set for backward compatibility
    )
    specialization = models.CharField(max_length=255, blank=True)
    qualifications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
