"""
URL routing for the hospital appointment booking system (appointment app).
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    AppointmentViewSet,
    AvailableClinicsView,
    AvailableDatesView,
    AvailableDoctorsView,
    AvailableTimeSlotsView,
    DoctorAppointmentListView,
)

app_name = "appointment"

router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path(
        "available-clinics/", AvailableClinicsView.as_view(), name="available-clinics"
    ),
    path(
        "available-doctors/", AvailableDoctorsView.as_view(), name="available-doctors"
    ),
    path("available-dates/", AvailableDatesView.as_view(), name="available-dates"),
    path("available-slots/", AvailableTimeSlotsView.as_view(), name="available-slots"),
    path(
        "doctor/",
        DoctorAppointmentListView.as_view(),
        name="doctor-appointments",
    ),
    path("", include(router.urls)),
]
