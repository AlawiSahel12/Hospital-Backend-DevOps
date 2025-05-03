"""
URL mappings for the records API.
"""

from django.urls import path

from records import views

app_name = "records"


urlpatterns = [
    path("create/", views.CreateRecordView.as_view(), name="create"),
    path("manage/<int:id>/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
    path("manage/", views.ManageRecordView.as_view(), name="manage"),
    path("", views.ListPatientRecordsView.as_view(), name="list"),
]
