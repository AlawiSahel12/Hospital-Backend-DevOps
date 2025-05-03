"""
Records models.
"""

from django.db import models

from profiles.models import DoctorProfile, PatientProfile


class MedicalRecord(models.Model):
    """
    Represents a medical record for a patient.
    """

    RECORD_TYPES_CHOICES = (
        ("radiology", "Radiology"),
        ("laboratory", "Laboratory"),
    )

    record_file = models.URLField()
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE,
        related_name="medical_records"
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="medical_records"
    )
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES_CHOICES)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    record_date = models.DateField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Medical record for {self.patient} with {self.doctor}"
