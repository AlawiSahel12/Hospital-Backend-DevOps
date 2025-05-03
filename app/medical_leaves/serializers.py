"""
Serializers for the record API View.
"""

from rest_framework import serializers

from medical_leaves.models import MedicalLeaveRecord


class MedicalLeaveRecordSerializer(serializers.ModelSerializer):
    """Serializer for the record object."""

    class Meta:
        model = MedicalLeaveRecord
        fields = "__all__"
        read_only_fields = ("id",)

    def create(self, validated_data):
        """Create and return a record."""
        request = self.context.get('request')
        user = request.user if request else None
        if user.is_staff:
            return MedicalLeaveRecord.objects.create(**validated_data)
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

            instance.from_date = validated_data.get(
                "from_date", instance.from_date)
            instance.to_date = validated_data.get("to_date", instance.to_date)
            instance.exams_included = validated_data.get(
                "exams_included", instance.exams_included)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError(
                "You do not have permission to update a record."
            )
