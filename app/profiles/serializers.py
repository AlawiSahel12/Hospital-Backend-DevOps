from django.contrib.auth import get_user_model

from rest_framework import serializers

from user.serializers import UserSerializer

from .models import DoctorProfile, PatientProfile


class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the PatientProfile model.
    """

    user = UserSerializer(read_only=True)
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = ["user", "user_id", "blood_type", "allergies", "illnesses"]
        read_only_fields = ["profile_id", "user", "created_at", "updated_at"]

    def get_user_id(self, obj):
        """
        Return the ID of the PatientProfile instance.
        """
        return obj.user.id


class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the DoctorProfile model.
    Anyone can read, but only staff can create/update.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            "doctor_name",
            "user",
            "specialization",
            "qualifications",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_doctor_name(self, obj):
        return str(obj)
