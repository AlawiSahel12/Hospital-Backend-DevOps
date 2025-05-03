"""Views for the profiles app."""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import DoctorProfile, PatientProfile
from .serializers import DoctorProfileSerializer, PatientProfileSerializer


class PatientProfileView(generics.RetrieveUpdateAPIView):
    """
    Self-service endpoint for patients to retrieve and update their own profile.
    Uses PATCH for partial updates. The profile is fetched based on request.user.
    """

    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the profile associated with the authenticated user.
        return PatientProfile.objects.get(user=self.request.user)


class AdminPatientProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only endpoint for listing all patient profiles.
    This endpoint is for development/testing and is secured by IsAdminUser.
    IsAdminUser checks that request.user.is_staff is True.
    """

    queryset = PatientProfile.objects.all()
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAdminUser]


class DoctorProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DoctorProfile:
      - GET requests (list and retrieve) are public.
      - POST, PATCH, PUT, and DELETE (soft delete) are restricted to admin users.
      - Soft delete: instead of removing the record, set `is_active` to False.
    """

    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    http_method_names = ["get", "post", "patch", "put", "delete", "head", "options"]

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            # Allow anyone (public access) for list and retrieve.
            return [permissions.AllowAny()]
        # All other methods require the user to be an admin.
        return [IsAdminUser()]

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Override the destroy method to perform a soft delete:
        Instead of deleting the record, mark it as inactive.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
