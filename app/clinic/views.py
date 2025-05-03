"""ViewSet for Clinic model."""

from rest_framework import permissions, viewsets

from .models import Clinic
from .serializers import ClinicSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class ClinicViewSet(viewsets.ModelViewSet):
    """Manage clinics in the database
    - List all clinics
    - Create a clinic
    - Update a clinic
    - Delete a clinic
    only staff users can create, update and delete clinics
    """

    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        """Track user who created/modified"""
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        """Track user who last modified"""
        serializer.save(last_modified_by=self.request.user)
