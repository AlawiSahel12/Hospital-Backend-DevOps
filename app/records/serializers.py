"""
Serializers for the record API View.
"""

from rest_framework import serializers

from records.models import MedicalRecord


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for the record object."""

    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Create and return a record."""
        request = self.context.get('request')
        user = request.user if request else None
        if user.is_staff:
            return MedicalRecord.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(
                "You do not have permission to create a record.")

    def update(self, instance, validated_data):
        """Update and return a record."""
        request = self.context.get('request')
        user = request.user if request else None
        if user.is_staff:
            instance.record_file = validated_data.get(
                "record_file", instance.record_file)
            instance.patient = validated_data.get("patient", instance.patient)
            instance.doctor = validated_data.get("doctor", instance.doctor)
            instance.record_type = validated_data.get(
                "record_type", instance.record_type)
            instance.details = validated_data.get("details", instance.details)
            instance.record_date = validated_data.get(
                "record_date", instance.record_date)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "You do not have permission to update a record."
            )
