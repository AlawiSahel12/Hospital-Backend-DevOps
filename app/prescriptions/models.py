from django.db import models

from appointment.models import Appointment
from profiles.models import DoctorProfile, PatientProfile


class PrescriptionRecord(models.Model):
    """
    Represents a prescription record for a patient.
    """

    PRESCRIPTION_STATUS_CHOICES = (
        ("active", "Active"),
        ("completed", "Completed"),
    )

    record_file = models.URLField()
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="prescription_records"
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="prescription_records"
    )

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="prescription_records"
    )

    prescription_status = models.CharField(
        max_length=10,
        choices=PRESCRIPTION_STATUS_CHOICES,
        default="active",
        help_text="Status of the prescription"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prescription ({self.prescription_status}) for {self.patient} by {self.doctor}"
