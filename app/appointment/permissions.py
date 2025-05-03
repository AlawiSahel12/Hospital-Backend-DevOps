# appointment/permissions.py

from rest_framework import permissions


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
