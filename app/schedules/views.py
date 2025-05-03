"""Views for the schedules app."""

from django.core.exceptions import ValidationError

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from schedules.models import DoctorSchedule
from schedules.serializers import (
    DoctorScheduleSerializer,
    RepeatedDoctorScheduleSerializer,
)


class IsStaffUser(permissions.BasePermission):
    """Staff-only for write operations, public read"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Public read
        return bool(request.user and request.user.is_staff)


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing doctor schedules.
    - Staff can create, update, delete schedules.
    - Public can read schedules.
    - Bulk creation of schedules is allowed.
    - Soft delete implementation.
    - Uses custom manager for active schedules.
    - Custom action for bulk creation of schedules.
    - Public endpoint for available time slots.

    """

    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsStaffUser]  # Staff-only for write operations, public read

    def get_queryset(self):
        """Return appropriate queryset based on user role"""
        if self.request.user.is_staff:
            # Staff sees all schedules through original manager
            return DoctorSchedule.all_objects.all()
        # Others see active future schedules through custom manager
        return DoctorSchedule.objects.all()

    @action(detail=False, methods=["post"], url_path="bulk")
    def bulk_create_schedules(self, request):
        """Handle bulk schedule creation with proper validation"""
        serializer = RepeatedDoctorScheduleSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            created = serializer.save()
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DoctorScheduleSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        """Soft delete implementation"""
        instance.is_active = False
        instance.save()

    def perform_create(self, serializer):
        serializer.save(last_modified_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_modified_by=self.request.user)
