"""URL Configuration for Clinic app"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import ClinicViewSet

app_name = "clinic"

router = DefaultRouter()
router.register("", ClinicViewSet, basename="clinic")

urlpatterns = [
    path("", include(router.urls)),
]
