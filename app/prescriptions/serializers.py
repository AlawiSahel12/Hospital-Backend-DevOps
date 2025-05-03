"""
Serializers for the record API View.
"""

from rest_framework import serializers

from prescriptions.models import PrescriptionRecord


class PrescriptionRecordSerializer(serializers.ModelSerializer):
    """Serializer for the record object."""

    doctor_name = serializers.SerializerMethodField()
    clinic_name = serializers.SerializerMethodField()

    class Meta:
        model = PrescriptionRecord
        fields = "__all__"
        read_only_fields = ("id",)

    def get_doctor_name(self, obj):
        """Return the doctor’s full name (falls back gracefully)."""
        user = getattr(obj.doctor, "user", None)
        if user and (user.first_name or user.last_name):
            return str(user)
        return str(obj.doctor)

    def get_clinic_name(self, obj):
        """Return the clinic name (falls back gracefully)."""
        return str(obj.appointment.clinic)

    def create(self, validated_data):
        """Create and return a record."""
        request = self.context.get("request")
        user = request.user if request else None
        if user.is_staff:
            return PrescriptionRecord.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(
                "You do not have permission to create a record."
            )

    def update(self, instance, validated_data):
        """Update and return a record."""
        request = self.context.get("request")
        user = request.user if request else None
        if user.is_staff:
            instance.record_file = validated_data.get(
                "record_file", instance.record_file
            )
            instance.patient = validated_data.get("patient", instance.patient)
            instance.doctor = validated_data.get("doctor", instance.doctor)

            instance.appointment = validated_data.get(
                "appointment", instance.appointment
            )
            instance.prescription_status = validated_data.get(
                "prescription_status", instance.prescription_status
            )
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "You do not have permission to update a record."
            )
