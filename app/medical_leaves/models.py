from django.db import models

from profiles.models import DoctorProfile, PatientProfile


class MedicalLeaveRecord(models.Model):
    """
    Represents a medical leave record for a patient.
    """

    record_file = models.URLField()
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="medical_leave_records"
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="medical_leave_records"
    )

    # Medical leave specific fields
    from_date = models.DateField()
    to_date = models.DateField()
    exams_included = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Medical leave for {self.patient} from {self.from_date} to {self.to_date}"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.from_date > self.to_date:
            raise ValidationError("from_date cannot be after to_date.")
