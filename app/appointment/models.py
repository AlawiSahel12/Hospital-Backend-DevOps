"""Appointment model for managing patient appointments in a clinic."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from clinic.models import Clinic
from schedules.models import DoctorSchedule

User = settings.AUTH_USER_MODEL


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELED = "canceled", "Canceled"
        RESCHEDULED = "rescheduled", "Rescheduled"

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        help_text="Patient who booked the appointment.",
    )
    # Denormalized fields for snapshot consistency.
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        help_text="Doctor associated with the appointment.",
        null=True,  # Will be auto-populated from schedule if not provided.
        blank=True,
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="Clinic where the appointment takes place.",
        null=True,
        blank=True,
    )
    schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.CASCADE,
        related_name="appointments",
        help_text="The schedule slot from which this appointment is booked.",
    )
    # Snapshot of schedule details
    date = models.DateField(
        help_text="Appointment date. Auto-populated from schedule if not provided.",
        null=True,
        blank=True,
    )
    start_time = models.TimeField(
        help_text="Appointment start time. Must exactly match one of the schedule’s available slots."
    )
    end_time = models.TimeField(
        help_text="Appointment end time. Must exactly match one of the schedule’s available slots."
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the appointment.",
    )
    appointment_type = models.CharField(
        max_length=20,
        choices=DoctorSchedule.APPOINTMENT_TYPE_CHOICES,
        default="physical",
        help_text="Type of appointment (physical or online). Auto-populated from schedule if not provided.",
    )
    cancellation_reason = models.TextField(
        blank=True, help_text="Reason for cancellation, if applicable."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "start_time"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["date", "start_time"]),
        ]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def clean(self):
        """
        Custom validation to ensure:
         - The appointment's time slot exactly matches one of the schedule's valid slots.
         - The appointment's date, doctor, clinic, and type are consistent with the schedule.
         - There is no double booking for active (pending/confirmed) appointments.
        """
        if not self.schedule:
            raise ValidationError("A schedule must be specified for the appointment.")

        # Auto-populate snapshot fields from the schedule if not already set.
        if not self.date:
            self.date = self.schedule.date
        if not self.doctor_id:
            self.doctor = self.schedule.doctor
        if not self.clinic_id:
            self.clinic = self.schedule.clinic
        if not self.appointment_type:
            self.appointment_type = self.schedule.appointment_type

        # Ensure the appointment date matches the schedule date.
        if self.date != self.schedule.date:
            raise ValidationError("Appointment date must match the schedule's date.")

        # Validate that the chosen time slot is one of the valid slots.
        valid_slots = self.schedule.get_time_slots()
        if (self.start_time, self.end_time) not in valid_slots:
            raise ValidationError("Invalid time slot for the selected schedule.")

        # Prevent double bookings for active appointments.
        # Define which statuses block the slot from being rebooked.
        blocking_statuses = [self.Status.PENDING, self.Status.CONFIRMED]
        conflicts = Appointment.objects.filter(
            schedule=self.schedule,
            start_time=self.start_time,
            end_time=self.end_time,
            status__in=blocking_statuses,
        ).exclude(pk=self.pk)
        if conflicts.exists():
            raise ValidationError("This time slot is already booked.")

        super().clean()

    def save(self, *args, **kwargs):
        # Run full model validation before saving.
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Appointment {self.id} for {self.patient} with {self.doctor} "
            f"on {self.date} at {self.start_time}"
        )
