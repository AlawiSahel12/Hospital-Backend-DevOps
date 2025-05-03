"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers

User = get_user_model()


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset.
    Expects an email address.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        value = value.strip().lower()
        if not User.objects.filter(email=value).exists():
            # For security, you may choose to always return success.
            # But here we raise an error to inform that no user exists.
            raise serializers.ValidationError(
                "No user is associated with this email address."
            )
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming a password reset with a token.
    Expects a base64-encoded UID, token, and new password.
    """

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        uidb64 = data.get("uid")
        token = data.get("token")
        try:
            # Decode the user ID from the URL-safe base64 encoding.
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid user identifier.")

        # Check token validity.
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError(
                "The reset token is invalid or has expired."
            )

        data["user"] = user
        return data

    def save(self, **kwargs):
        """Set the new password on the user and return the user instance."""
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the user object.
    """

    # Explicitly define the date_of_birth field with custom input formats and error message.
    date_of_birth = serializers.DateField(
        input_formats=["%Y-%m-%d"],  # Only accept dates in this format.
        required=True,
        allow_null=True,
        error_messages={"invalid": "Date of birth must be in the format YYYY-MM-DD."},
    )

    class Meta:
        model = get_user_model()
        # Only these fields are returned in GET responses.
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "date_of_birth",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate_date_of_birth(self, value):
        """
        Additional validation to ensure date_of_birth is not in the future.
        (Optional: Remove or adjust this check based on your requirements.)
        """
        today = timezone.now().date()
        if value > today:
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
