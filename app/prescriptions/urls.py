"""
URL mappings for the prescriptions API.
"""

from django.urls import path

from prescriptions import views

app_name = "prescriptions"


urlpatterns = [
    path("create/", views.CreateRecordView.as_view(), name="create"),
    path("manage/<int:id>/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
    path("manage/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
]
