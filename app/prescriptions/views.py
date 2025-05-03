"""
Views for the records API.
"""

from rest_framework import generics, status
from rest_framework.response import Response

from prescriptions.serializers import PrescriptionRecordSerializer

from .models import PatientProfile, PrescriptionRecord


class CreateRecordView(generics.CreateAPIView):
    """Create a new record in the system."""
    serializer_class = PrescriptionRecordSerializer

    def upload_file(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ManageRecordView(generics.UpdateAPIView):
    """Manage the authenticated record."""
    serializer_class = PrescriptionRecordSerializer

    def update(self, request, *args, **kwargs):
        record_id = self.kwargs.get('id')
        if not PrescriptionRecord.objects.filter(id=record_id).exists():
            return Response({"error": "Record not found."},
                            status=status.HTTP_404_NOT_FOUND)
        instance = PrescriptionRecord.objects.get(id=record_id)
        serializer = self.get_serializer(instance, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPatientRecordsView(generics.ListAPIView):
    """
    List all records for a specific patient (given by patient_id in the URL).
    """
    serializer_class = PrescriptionRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return PrescriptionRecord.objects.all()
        elif user.is_authenticated:
            # get patient profile id with specific user id
            patient_id = PatientProfile.objects.get(user=user.id).id
            return PrescriptionRecord.objects.filter(patient=patient_id)
        return []
