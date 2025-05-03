# appointment/permissions.py

from rest_framework import permissions

from profiles.models import DoctorProfile


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow unrestricted read (GET, HEAD, OPTIONS)
    but only staff can write (POST, PUT, PATCH, DELETE).
    """

    def has_permission(self, request, view):
        # SAFE_METHODS -> GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsDoctor(permissions.BasePermission):
    """
    Allows access only to authenticated users who have an *active* DoctorProfile.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return DoctorProfile.objects.filter(user=user, is_active=True).exists()
