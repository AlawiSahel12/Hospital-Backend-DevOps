"""
Views for the user API.
"""

# user/views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer

from .serializers import PasswordResetConfirmSerializer, PasswordResetRequestSerializer

# Import the Celery task
from .tasks import send_password_reset_email_task


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system.
    PatientProfile is automatically created via the signal.
    """

    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user instance."""
        return self.request.user


User = get_user_model()


class PasswordResetRequestView(APIView):
    """
    Handle a password reset request.
    Accepts an email address, verifies that a user exists, and sends a password reset email.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.get(email=email)

        # Generate token and uid for password reset.
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Instead of sending the email synchronously, invoke the Celery task.
        send_password_reset_email_task.delay(user.id, email, uid, token)

        # For security reasons, always return a success response.
        return Response(
            {
                "detail": "If an account exists for this email, a password reset link has been sent."
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    """
    Handle password reset confirmation.
    Accepts a uid, token, and new password, then resets the password if valid.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK,
        )
