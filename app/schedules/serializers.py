"""Serializers for the schedules app."""

import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from rest_framework import serializers

from clinic.models import Clinic
from schedules.models import DoctorSchedule


class WeekdayField(serializers.CharField):
    """
    Custom field to accept a single letter representing a weekday:
    M, T, W, R, F, S, U
    -> mapping to Python's weekday() integers: Monday=0 ... Sunday=6
    """

    VALID_WEEKDAYS = {
        "m": 0,
        "t": 1,
        "w": 2,
        "r": 3,
        "f": 4,
        "s": 5,
        "u": 6,
    }  # Lowercase keys

    def to_internal_value(self, data):
        data = str(data).lower().strip()  # Normalize to lowercase
        if data not in self.VALID_WEEKDAYS:
            raise serializers.ValidationError(
                f"Invalid weekday '{data}'. Valid: {list(self.VALID_WEEKDAYS.keys())}"
            )
        return self.VALID_WEEKDAYS[data]

    def to_representation(self, value):
        # Convert integer back to letter.
        for letter, num in self.VALID_WEEKDAYS.items():
            if num == value:
                return letter
        return str(value)


class DoctorScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for DoctorSchedule objects.
    Includes a computed read-only field for available time slots.
    """

    available_time_slots = serializers.SerializerMethodField()

    def validate(self, attrs):
        """Enforce model validation rules"""
        # Create temp instance for validation
        instance = DoctorSchedule(**attrs)

        # Manually set the PK if updating
        if self.instance:
            instance.pk = self.instance.pk

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

    class Meta:
        model = DoctorSchedule
        fields = [
            "id",
            "doctor",
            "clinic",
            "date",
            "start_time",
            "end_time",
            "slot_duration",
            "appointment_type",
            "is_active",
            "created_at",
            "updated_at",
            "available_time_slots",
            "last_modified_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "available_time_slots",
            "last_modified_by",
        ]

    def get_available_time_slots(self, obj):
        """
        Return a list of available time slots for this schedule.
        Each slot is "HH:MM:SS - HH:MM:SS".
        """
        slots = obj.get_available_time_slots()
        return [f"{s[0]} - {s[1]}" for s in slots]


class RepeatedDoctorScheduleSerializer(serializers.Serializer):
    """
    Serializer for creating repeated doctor schedules (bulk) over a date range.
    Example input:
      {
         "doctor": <user_id_of_doctor>,
         "clinic": <clinic_id>,
         "start_date": "2025-02-20",
         "end_date": "2025-05-01",
         "weekdays": ["U", "T", "R"],   # Sunday, Tuesday, Thursday
         "start_time": "09:00",
         "end_time": "18:00",
         "slot_duration": 60,
         "appointment_type": "physical"
      }
    """

    APPOINTMENT_TYPE_CHOICES = (
        ("physical", "Physical"),
        ("online", "Online"),
    )

    doctor = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.filter(doctor_profile__isnull=False),
        help_text="User ID of a user who has a DoctorProfile.",
    )
    clinic = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    weekdays = serializers.ListField(child=WeekdayField())
    start_time = serializers.TimeField()
    end_time = serializers.TimeField()
    slot_duration = serializers.IntegerField(min_value=1)
    appointment_type = serializers.ChoiceField(choices=APPOINTMENT_TYPE_CHOICES)

    def validate(self, data):
        # Ensure start_date <= end_date
        if data["start_date"] > data["end_date"]:
            raise serializers.ValidationError(
                "start_date must be before or equal to end_date."
            )
        # Ensure start_time < end_time
        if data["start_time"] >= data["end_time"]:
            raise serializers.ValidationError(
                "start_time must be strictly before end_time."
            )
        return data

    def create(self, validated_data):
        """Handle bulk creation with proper time validation"""
        schedules = []
        current_date = validated_data["start_date"]

        while current_date <= validated_data["end_date"]:
            if current_date.weekday() in validated_data["weekdays"]:
                # Create temporary instance for validation
                temp_schedule = DoctorSchedule(
                    doctor=validated_data["doctor"],
                    clinic=validated_data["clinic"],
                    date=current_date,
                    start_time=validated_data["start_time"],
                    end_time=validated_data["end_time"],
                    slot_duration=validated_data["slot_duration"],
                    appointment_type=validated_data["appointment_type"],
                )

                try:
                    # Validate against model constraints
                    temp_schedule.full_clean()
                    schedules.append(temp_schedule)
                except ValidationError as e:
                    if "overlap" not in e.message_dict:
                        raise

            current_date += datetime.timedelta(days=1)

        return DoctorSchedule.all_objects.bulk_create(schedules)
