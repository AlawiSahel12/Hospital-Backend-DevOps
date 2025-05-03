"""URL Configuration for the schedules app"""

# urls.py (new)
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import DoctorScheduleViewSet

router = DefaultRouter()
router.register(r"", DoctorScheduleViewSet, basename="schedule")

urlpatterns = [
    path("", include(router.urls)),
]
