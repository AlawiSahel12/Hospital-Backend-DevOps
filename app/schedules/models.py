"""Models for the schedules app."""

import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from clinic.models import Clinic


class DoctorScheduleManager(models.Manager):
    def get_queryset(self):
        today = datetime.date.today()
        return super().get_queryset().filter(is_active=True, date__gte=today)


class DoctorSchedule(models.Model):
    """
    Represents a doctor’s available shift or schedule for
    a specific date, time range, and clinic.
    - Appointment type stored here determines if it's "online" or "physical".
    """

    objects = DoctorScheduleManager()  # Custom manager
    all_objects = models.Manager()  # For staff access to all records

    APPOINTMENT_TYPE_CHOICES = (
        ("physical", "Physical"),
        ("online", "Online"),
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schedules"
    )
    clinic = models.ForeignKey(
        Clinic, on_delete=models.CASCADE, related_name="schedules"
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    slot_duration = models.PositiveIntegerField(
        help_text="Duration in minutes for each appointment slot."
    )

    appointment_type = models.CharField(
        max_length=20,
        choices=APPOINTMENT_TYPE_CHOICES,
        default="physical",
        help_text="Indicates whether this schedule is for\
            online or physical appointments.",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="modified_schedules",
    )

    class Meta:
        ordering = ["date", "start_time"]
        indexes = [
            models.Index(fields=["date", "is_active"]),
            models.Index(fields=["doctor", "clinic"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["appointment_type"]),
        ]

    def __str__(self):
        return f"Schedule for {self.doctor} on {self.date} @ {self.clinic.name}"

    def clean(self):
        """Validate schedule timing and conflicts"""
        now = datetime.datetime.now()
        schedule_end = datetime.datetime.combine(self.date, self.end_time)
        if schedule_end < now:
            raise ValidationError("Cannot create schedule in the past")

        # Check for overlapping schedules (existing logic)
        overlapping = DoctorSchedule.all_objects.filter(
            doctor=self.doctor,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError("Overlapping schedule exists")

    def get_time_slots(self):
        slots = []
        current_dt = datetime.datetime.combine(self.date, self.start_time)
        end_dt = datetime.datetime.combine(self.date, self.end_time)
        delta = datetime.timedelta(minutes=self.slot_duration)

        while current_dt < end_dt:  # Changed to < instead of <=
            slot_end = current_dt + delta
            if slot_end > end_dt:
                break  # Skip partial slots
            slots.append((current_dt.time(), slot_end.time()))
            current_dt = slot_end
        return slots

    def get_available_time_slots(self):
        """
        Return only the free slots for this schedule where no pending or confirmed appointment exists.
        """
        from appointment.models import (  # ✅ Local import to avoid circular import
            Appointment,
        )

        all_slots = self.get_time_slots()
        blocking_statuses = [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
        booked_slots = [
            (appt.start_time, appt.end_time)
            for appt in self.appointments.filter(status__in=blocking_statuses)
        ]
        return [slot for slot in all_slots if slot not in booked_slots]
