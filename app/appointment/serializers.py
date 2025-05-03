"""
Serializers for the hospital appointment booking system.
"""

from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers

from appointment.models import Appointment
from profiles.models import DoctorProfile
from schedules.models import DoctorSchedule


class AppointmentSerializer(serializers.ModelSerializer):
    # Auto-populated/read-only fields.
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    doctor = serializers.PrimaryKeyRelatedField(read_only=True)
    clinic = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.DateField(read_only=True)
    end_time = serializers.TimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    appointment_type = serializers.CharField(read_only=True)
    cancellation_reason = serializers.CharField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "clinic",
            "schedule",
            "date",
            "start_time",
            "end_time",
            "status",
            "appointment_type",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]

    def validate_schedule(self, value):
        """
        Ensure the selected schedule is active and not in the past.
        """
        if not value.is_active:
            raise serializers.ValidationError("The selected schedule is not active.")

        # Combine schedule date and end_time to verify it is in the future.
        schedule_end_dt = datetime.combine(value.date, value.end_time)
        # If the datetime is naive, assume the current timezone.
        schedule_end_dt = timezone.make_aware(schedule_end_dt)
        if schedule_end_dt < timezone.now():
            raise serializers.ValidationError("Cannot book a schedule in the past.")
        return value

    def validate(self, data):
        """
        Validate that:
          - A schedule and start_time are provided.
          - The computed end_time (start_time + slot_duration) matches one of the schedule's valid slots.
          - The selected slot is available.
        """
        schedule = data.get("schedule")
        start_time = data.get("start_time")
        if not schedule:
            raise serializers.ValidationError({"schedule": "This field is required."})
        if not start_time:
            raise serializers.ValidationError({"start_time": "This field is required."})

        # Calculate the expected end_time from the schedule's slot_duration.
        computed_end_time = (
            datetime.combine(schedule.date, start_time)
            + timedelta(minutes=schedule.slot_duration)
        ).time()

        # Validate that the (start_time, computed_end_time) tuple is one of the schedule's valid slots.
        valid_slots = schedule.get_time_slots()
        if (start_time, computed_end_time) not in valid_slots:
            raise serializers.ValidationError(
                "Invalid time slot for the selected schedule."
            )

        # Validate that the slot is available (i.e. not already booked).
        available_slots = schedule.get_available_time_slots()
        if (start_time, computed_end_time) not in available_slots:
            raise serializers.ValidationError("Selected time slot is not available.")

        # Pass the computed end_time forward for use in create().
        data["computed_end_time"] = computed_end_time
        return data

    @transaction.atomic
    def create(self, validated_data):
        # Pop the computed end_time from validated_data.
        computed_end_time = validated_data.pop("computed_end_time")
        schedule = validated_data["schedule"]

        # Auto-populate related fields from the schedule.
        validated_data["patient"] = self.context["request"].user
        validated_data["doctor"] = schedule.doctor
        validated_data["clinic"] = schedule.clinic
        validated_data["date"] = schedule.date
        validated_data["appointment_type"] = schedule.appointment_type
        validated_data["end_time"] = computed_end_time

        # Automatically confirm the appointment if all validations pass.
        validated_data["status"] = Appointment.Status.CONFIRMED

        return super().create(validated_data)


class ChatSessionMixin(serializers.Serializer):
    chat_session_id = serializers.SerializerMethodField()

    def get_chat_session_id(self, obj):
        # obj is Appointment
        session = getattr(obj, "chat_session", None)  # reverse FK
        return session.pk if session else None


class AppointmentReadSerializer(ChatSessionMixin, serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    clinic_name = serializers.ReadOnlyField(source="clinic.name")

    class Meta:
        model = Appointment

        fields = [
            "id",
            "doctor_id",
            "patient_id",
            "clinic_id",
            "doctor_name",
            "patient_name",
            "clinic_name",
            "date",
            "start_time",
            "appointment_type",
            "status",
            "chat_session_id",
        ]

    def get_doctor_name(self, obj):
        # Use the doctor name from the DoctorProfile model.
        return str(obj.doctor) if obj.doctor else None

    def get_patient_name(self, obj):
        return str(obj.patient) if obj.patient else None


class RescheduleSerializer(serializers.Serializer):
    new_schedule = serializers.PrimaryKeyRelatedField(
        queryset=DoctorSchedule.objects.all()
    )
    new_start_time = serializers.TimeField()

    def validate(self, data):
        """
        Validate the new schedule and new_start_time.
        Computes the new end time and ensures the slot is valid and available.
        """
        new_schedule = data["new_schedule"]
        new_start_time = data["new_start_time"]

        new_end_time = (
            datetime.combine(new_schedule.date, new_start_time)
            + timedelta(minutes=new_schedule.slot_duration)
        ).time()

        valid_slots = new_schedule.get_time_slots()
        if (new_start_time, new_end_time) not in valid_slots:
            raise serializers.ValidationError(
                "Invalid time slot for the selected schedule."
            )

        available_slots = new_schedule.get_available_time_slots()
        if (new_start_time, new_end_time) not in available_slots:
            raise serializers.ValidationError("Selected time slot is not available.")

        data["new_end_time"] = new_end_time
        return data


class CancelAppointmentSerializer(serializers.Serializer):
    # Allows an optional cancellation reason to be provided.
    reason = serializers.CharField(required=False, allow_blank=True)


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for the doctor's profile information"""

    class Meta:
        model = DoctorProfile
        fields = ["specialization", "qualifications"]


class DoctorSerializer(serializers.ModelSerializer):
    """Public-facing serializer for doctor information"""

    profile = DoctorProfileSerializer(source="doctor_profile")

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email", "profile"]
