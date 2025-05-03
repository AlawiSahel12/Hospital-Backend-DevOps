"""Serializers for the Dependent model."""

import re

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers

from .models import Dependent

User = User = get_user_model()


class DependentSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and retrieving dependent details.
    Also provides a computed field 'has_account' that indicates if an account is linked.
    """

    has_account = serializers.SerializerMethodField()
    account_email = serializers.EmailField(
        source="account.email", read_only=True, help_text="Email of the linked account."
    )
    account_id = serializers.IntegerField(
        source="account.id", read_only=True, help_text="ID of the linked account."
    )

    class Meta:
        model = Dependent
        fields = [
            "id",
            "guardian",
            "first_name",
            "middle_name",
            "last_name",
            "national_id",
            "relationship",
            "date_of_birth",
            "account_id",
            "account_email",
            "has_account",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "has_account", "created_at", "updated_at"]

    def validate_national_id(self, value):
        """
        Ensure that the national_id consists of exactly 10 digits.
        """
        if not re.fullmatch(r"\d{10}", value):
            raise serializers.ValidationError(
                "National ID must consist of exactly 10 digits."
            )
        return value

    def validate_date_of_birth(self, value):
        """
        Ensure the date of birth is not in the future.
        """
        if value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def get_has_account(self, obj):
        return obj.account is not None


class DependentInvitationSerializer(serializers.Serializer):
    """
    Serializer for validating invitation input when inviting a dependent.

    Expected input:
      - dependent_id: The ID of the dependent to invite (must belong to the authenticated guardian).
      - email: The invitation email address which should be unique in the system.
        An email already in use is disallowed except when it belongs to the dependent’s existing account.
    """

    dependent_id = serializers.IntegerField(help_text="ID of the dependent to invite.")
    email = serializers.EmailField(
        help_text="Invitation email address for the dependent."
    )

    def validate(self, data):
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Request context is missing.")
        guardian = request.user
        invite_email = data.get("email").strip().lower()

        # Ensure the dependent exists and belongs to the guardian.
        try:
            dependent = Dependent.objects.get(
                id=data.get("dependent_id"), guardian=guardian
            )
        except Dependent.DoesNotExist:
            raise serializers.ValidationError(
                "Dependent not found or you are not authorized to invite this dependent."
            )

        # Check if the invitation email is already registered in the system.
        existing_user = User.objects.filter(email=invite_email).first()
        if existing_user:
            # If the dependent already has an account...
            if dependent.account:
                # ...allow the email if it matches the previously registered dependent account.
                if existing_user.pk != dependent.account.pk:
                    raise serializers.ValidationError(
                        "This email is already registered for a different account."
                    )
            else:
                # If no account is linked yet to the dependent, do not allow an email that is already used.
                raise serializers.ValidationError(
                    "This email is already registered in the system."
                )

        # Attach the dependent instance and normalized email.
        data["dependent"] = dependent
        data["email"] = invite_email
        return data
