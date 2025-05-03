"""
Views for the records API.
"""

from rest_framework import generics, status
from rest_framework.response import Response

from records.serializers import MedicalRecordSerializer

from .models import MedicalRecord, PatientProfile


class CreateRecordView(generics.CreateAPIView):
    """Create a new record in the system."""
    serializer_class = MedicalRecordSerializer

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
    serializer_class = MedicalRecordSerializer

    def update(self, request, *args, **kwargs):
        record_id = self.kwargs.get('id')
        if not MedicalRecord.objects.filter(id=record_id).exists():
            return Response({"error": "Record not found."},
                            status=status.HTTP_404_NOT_FOUND)
        instance = MedicalRecord.objects.get(id=record_id)
        serializer = self.get_serializer(instance, data=request.data)
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPatientRecordsView(generics.ListAPIView):
    """
    List all records for a specific patient (given by patient_id in the URL).
    """
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        user = self.request.user
        record_type = self.request.query_params.get("record_type")

        if user.is_staff:
            return MedicalRecord.objects.all()
        elif user.is_authenticated:
            # get patient profile id with specific user id
            patient_id = PatientProfile.objects.get(user=user.id).id
            if record_type:
                return MedicalRecord.objects.filter(
                    patient=patient_id, record_type=record_type)
            else:
                # get all records for the specific patient
                return MedicalRecord.objects.filter(patient=patient_id)
        return []
