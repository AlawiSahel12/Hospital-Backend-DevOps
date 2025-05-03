"""
Views for the delivery API.
"""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from delivery.serializers import DeliveryRequestSerializer

from .models import Address, DeliveryRequest, PatientProfile
from .serializers import AddressSerializer


class CreateDeliveryView(generics.CreateAPIView):
    """Create a new delivery."""

    serializer_class = DeliveryRequestSerializer

    def create(self, request, *args, **kwargs):
        """Create a new delivery."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageDeliveryView(generics.UpdateAPIView):
    """Manage the authenticated delivery."""

    serializer_class = DeliveryRequestSerializer

    def update(self, request, *args, **kwargs):
        """Manage the authenticated delivery."""
        request_id = self.kwargs.get("id")
        if not DeliveryRequest.objects.filter(id=request_id).exists():
            return Response(
                {"error": "Request Delivery not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        instance = DeliveryRequest.objects.get(id=request_id)
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListDeliveryView(generics.ListAPIView):
    """List all deliveries."""

    serializer_class = DeliveryRequestSerializer

    def get_queryset(self):
        user = self.request.user
        prescription_id = self.request.query_params.get("prescription", None)
        if user.is_staff:
            return DeliveryRequest.objects.all()
        elif user.is_authenticated:
            # get patient profile id with specific user id
            patient_id = PatientProfile.objects.get(user=user.id).id
            if prescription_id:
                # filter by prescription id
                return DeliveryRequest.objects.filter(
                    patient=patient_id, prescription=prescription_id
                )
            return DeliveryRequest.objects.filter(patient=patient_id)
        return []


class AddressViewSet(viewsets.ModelViewSet):
    """
    /api/addresses/          → list, create
    /api/addresses/{pk}/     → retrieve, update, delete
    /api/addresses/{pk}/set-default/  → POST to make this address the default
    """

    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save()  # user injected in serializer.create()
