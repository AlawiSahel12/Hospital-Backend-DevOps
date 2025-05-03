"""URL configuration for dependents app"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import AdminDependentViewSet, DependentViewSet

router = DefaultRouter()
# Endpoint for guardians managing their own dependents.
router.register(r"", DependentViewSet, basename="dependent")
# Separate admin endpoint for creating, updating, listing, and retrieving any dependent.
router.register(r"admin", AdminDependentViewSet, basename="admin-dependent")

urlpatterns = [
    path("", include(router.urls)),
]
