from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import AdminPatientProfileViewSet, DoctorProfileViewSet, PatientProfileView

app_name = "profiles"

router = DefaultRouter()
router.register(r"doctor", DoctorProfileViewSet, basename="doctor-profile")
router.register(
    r"admin-profiles", AdminPatientProfileViewSet, basename="admin-patient-profiles"
)


urlpatterns = [
    path("", include(router.urls)),
    path("my-profile/", PatientProfileView.as_view(), name="my-patient-profile"),
]
