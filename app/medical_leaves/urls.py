"""
URL mappings for the medical leaves API.
"""

from django.urls import path

from medical_leaves import views

app_name = "medical_leaves"


urlpatterns = [
    path("create/", views.CreateRecordView.as_view(), name="create"),
    path("manage/<int:id>/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
    path("manage/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
]
