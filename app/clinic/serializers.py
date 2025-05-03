"""Serializers for the Clinic model."""

from rest_framework import serializers

from .models import Clinic


class ClinicSerializer(serializers.ModelSerializer):
    """
    Serializer for Clinic objects.
    """

    class Meta:
        model = Clinic
        fields = [
            "id",
            "name",
            "name_ar",
            "description",
            "logo",
            "created_at",
            "updated_at",
            "last_modified_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "last_modified_by",  # Auto-populated
        ]
