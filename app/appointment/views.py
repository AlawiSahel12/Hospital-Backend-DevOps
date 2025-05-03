"""
Views for the hospital appointment booking system.
"""

import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from clinic.models import Clinic
from clinic.serializers import ClinicSerializer
from profiles.models import DoctorProfile
from schedules.models import DoctorSchedule
from schedules.serializers import DoctorScheduleSerializer

from .models import Appointment
from .permissions import IsDoctor
from .serializers import (
    AppointmentReadSerializer,
    AppointmentSerializer,
    DoctorSerializer,
    RescheduleSerializer,
)

# from django.utils import timezone
# from datetime import timedelta


class AvailableClinicsView(APIView):
    """
    Returns list of clinics with active schedules for a given appointment type
    Example: /api/appointments/available-clinics/?type=physical
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        appointment_type = request.query_params.get("type")

        # Validate appointment type
        if not appointment_type:
            return Response(
                {"detail": "Query parameter 'type' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment_type not in ["physical", "online"]:
            return Response(
                {"detail": "Invalid appointment type. Use 'physical' or 'online'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get current date-aware datetime for time comparison
        now = datetime.datetime.now()

        # Get clinic IDs with active schedules matching criteria
        clinic_ids = (
            DoctorSchedule.objects.filter(
                appointment_type=appointment_type, is_active=True, date__gte=now.date()
            )
            .exclude(date=now.date(), end_time__lte=now.time())
            .values_list("clinic_id", flat=True)
            .distinct()
        )

        # Get unique clinics
        clinics = Clinic.objects.filter(id__in=clinic_ids)
        serializer = ClinicSerializer(clinics, many=True)

        return Response(serializer.data)


class AvailableDoctorsView(APIView):
    """
    Returns list of doctors with active schedules for given clinic and appointment type
    Example: /api/appointments/available-doctors/?clinic_id=1&type=physical
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        clinic_id = request.query_params.get("clinic_id")
        appointment_type = request.query_params.get("type")

        # Validate parameters
        if not clinic_id or not appointment_type:
            return Response(
                {"detail": "Both 'clinic_id' and 'type' parameters are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment_type not in ["physical", "online"]:
            return Response(
                {"detail": "Invalid appointment type. Use 'physical' or 'online'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate clinic exists
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {"detail": "Invalid clinic ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get current datetime for time comparison
        now = datetime.datetime.now()

        # Get doctors with active schedules
        doctor_ids = (
            DoctorSchedule.objects.filter(
                clinic=clinic,
                appointment_type=appointment_type,
                is_active=True,
                date__gte=now.date(),
            )
            .exclude(date=now.date(), end_time__lte=now.time())
            .values_list("doctor", flat=True)
            .distinct()
        )

        # Get active doctors with profiles
        doctors = (
            get_user_model()
            .objects.filter(
                id__in=doctor_ids,
                doctor_profile__isnull=False,
                doctor_profile__is_active=True,
            )
            .select_related("doctor_profile")
        )

        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data)


class AvailableDatesView(APIView):
    """
    Returns list of available dates for appointments
    given doctor_id, clinic_id, and appointment_type
    Example: /api/appointments/available-dates/?doctor_id=1&clinic_id=1&type=physical
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        doctor_id = request.query_params.get("doctor_id")
        clinic_id = request.query_params.get("clinic_id")
        appointment_type = request.query_params.get("type")

        # Validate required parameters
        if not all([doctor_id, clinic_id, appointment_type]):
            return Response(
                {"detail": "doctor_id, clinic_id, and type parameters are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment_type not in ["physical", "online"]:
            return Response(
                {"detail": "Invalid appointment type. Use 'physical' or 'online'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate clinic exists
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {"detail": "Invalid clinic ID"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Validate doctor exists
        if not DoctorProfile.objects.filter(user_id=doctor_id, is_active=True).exists():
            return Response(
                {"detail": "No active doctor found with this ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get current datetime for time comparison
        now = datetime.datetime.now()

        # Get active schedules with available slots
        schedules = (
            DoctorSchedule.objects.filter(
                doctor=doctor_id,
                clinic=clinic,
                appointment_type=appointment_type,
                is_active=True,
                date__gte=now.date(),
            )
            .exclude(date=now.date(), end_time__lte=now.time())
            .prefetch_related("appointments")
        )

        # Collect dates with available slots
        available_dates = []
        for schedule in schedules:
            if schedule.get_available_time_slots():
                available_dates.append(schedule.date)

        # Return unique sorted dates
        unique_dates = sorted(list(set(available_dates)))
        return Response([date.isoformat() for date in unique_dates])


class AvailableTimeSlotsView(APIView):
    """
    Returns all available schedules (with their available time slots) for a doctor/clinic/date/appointment-type combo.
    GET /api/appointments/available-slots/?doctor_id=1&clinic_id=1&type=physical&date=2025-06-20
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Parse and validate parameters
        doctor_id = request.query_params.get("doctor_id")
        clinic_id = request.query_params.get("clinic_id")
        appointment_type = request.query_params.get("type")
        date_str = request.query_params.get("date")

        # Validate required parameters
        if not all([doctor_id, clinic_id, appointment_type, date_str]):
            return Response(
                {
                    "detail": "Missing required parameters: doctor_id, clinic_id, type, date"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate appointment type
        if appointment_type not in ["physical", "online"]:
            return Response(
                {"detail": "Invalid appointment type. Use 'physical' or 'online'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date format
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate clinic exists
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {"detail": "Invalid clinic ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate active doctor profile
        if not DoctorProfile.objects.filter(user_id=doctor_id, is_active=True).exists():
            return Response(
                {"detail": "No active doctor found with this ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Optimize: if the date is today, only include schedules that haven't ended.
        now = datetime.datetime.now()
        time_filter = {}
        if date_obj == now.date():
            time_filter["end_time__gt"] = now.time()

        # Get schedules matching criteria
        schedules = (
            DoctorSchedule.objects.filter(
                doctor=doctor_id,
                clinic=clinic,
                appointment_type=appointment_type,
                date=date_obj,
                is_active=True,
                **time_filter,
            )
            .prefetch_related("appointments")
            .order_by("start_time")
        )

        serializer = DoctorScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AppointmentPermission(permissions.BasePermission):
    """
    Object-level permission: only the patient or the doctor associated with the appointment can access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user or obj.doctor == request.user


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD endpoints for appointments plus custom actions for canceling and rescheduling.
    """

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, AppointmentPermission]

    http_method_names = ["get", "post"]  # Limit the allowed methods

    def get_queryset(self):
        user = self.request.user
        qs = Appointment.objects.all().select_related(
            "schedule", "doctor", "clinic", "patient"
        )
        # Filter by role: patients see only their appointments; doctors see assigned appointments.
        if hasattr(user, "role"):
            if user.role == "patient":
                qs = qs.filter(patient=user)
            elif user.role == "doctor":
                qs = qs.filter(doctor=user)
        else:
            qs = qs.none()

        # Allow filtering via query parameters.
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)
        appointment_type_filter = self.request.query_params.get("appointment_type")
        if appointment_type_filter:
            qs = qs.filter(appointment_type__iexact=appointment_type_filter)
        return qs.order_by("-created_at")

    def get_object(self):
        # Retrieve the object from the full set, then check permissions.
        queryset = (
            Appointment.objects.all()
        )  # Return all appointments regardless of user
        obj = get_object_or_404(queryset, pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        # Use the read serializer for GET requests.
        if self.request.method in ["GET"]:
            return AppointmentReadSerializer
        return AppointmentSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            schedule = serializer.validated_data["schedule"]
            # Lock the schedule to prevent race conditions.
            DoctorSchedule.objects.select_for_update().get(pk=schedule.pk)
            serializer.save()

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        """
        Cancel an appointment, which frees up the associated time slot.
        Optionally accepts a cancellation reason.
        """
        appointment = self.get_object()

        # # Combine appointment's date and start_time into a single datetime.
        # appt_datetime = datetime.combine(appointment.date, appointment.start_time)
        # # Convert to an aware datetime if using time zones.
        # appt_datetime = timezone.make_aware(
        #     appt_datetime, timezone.get_current_timezone()
        # )

        # now = timezone.now()
        # # Calculate time difference
        # time_until_appointment = appt_datetime - now

        # # Enforce the 12-hour restriction
        # if time_until_appointment < timedelta(hours=12):
        #     return Response(
        #         {
        #             "detail": "You cannot cancel an appointment less than 12 hours before its start time."
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # Check that the appointment is not already canceled or completed.
        if appointment.status in [
            Appointment.Status.CANCELED,
            Appointment.Status.COMPLETED,
        ]:
            return Response(
                {"detail": "Appointment is already canceled or completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cancellation_reason = request.data.get("cancellation_reason", "")
        appointment.status = Appointment.Status.CANCELED
        appointment.cancellation_reason = cancellation_reason
        appointment.save()
        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reschedule")
    def reschedule(self, request, pk=None):
        """
        Reschedule an appointment:
          1. Validates the new schedule/slot using RescheduleSerializer.
          2. Creates a new appointment in the new slot.
          3. Updates the original appointment's status to 'rescheduled'.
        All actions are wrapped in an atomic transaction.
        """
        original_appointment = self.get_object()

        # # Combine date and time for the original appointment
        # appt_datetime = datetime.combine(
        #     original_appointment.date, original_appointment.start_time
        # )
        # appt_datetime = timezone.make_aware(
        #     appt_datetime, timezone.get_current_timezone()
        # )

        # now = timezone.now()
        # time_until_appointment = appt_datetime - now
        # if time_until_appointment < timedelta(hours=12):
        #     return Response(
        #         {
        #             "detail": "You cannot reschedule an appointment less than 12 hours before its start time."
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        if original_appointment.status != Appointment.Status.CONFIRMED:
            return Response(
                {"detail": "Only confirmed appointments can be rescheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RescheduleSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_schedule = serializer.validated_data["new_schedule"]
        new_start_time = serializer.validated_data["new_start_time"]
        new_end_time = serializer.validated_data["new_end_time"]

        with transaction.atomic():
            # Lock both the original and new schedules to avoid race conditions.
            DoctorSchedule.objects.select_for_update().filter(
                pk__in=[original_appointment.schedule.pk, new_schedule.pk]
            )
            # Create the new appointment using our AppointmentSerializer (which auto-populates snapshot fields).
            new_data = {
                "schedule": new_schedule.pk,
                "start_time": new_start_time,
                "end_time": new_end_time,
            }
            new_appt_serializer = AppointmentSerializer(
                data=new_data, context={"request": request}
            )
            new_appt_serializer.is_valid(raise_exception=True)
            new_appointment = new_appt_serializer.save()
            # Mark the original appointment as rescheduled.
            original_appointment.status = Appointment.Status.RESCHEDULED
            original_appointment.save()

        response_data = {
            "original": self.get_serializer(original_appointment).data,
            "new": self.get_serializer(new_appointment).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class DoctorAppointmentListView(generics.ListAPIView):
    """
    GET /api/appointments/doctor-list/
    Returns appointments where request.user is the assigned doctor.
    Supports ?status=<status>&appointment_type=<type> like the main ViewSet.
    """

    serializer_class = AppointmentReadSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_queryset(self):
        qs = (
            Appointment.objects.filter(doctor=self.request.user)
            .select_related("patient", "clinic", "schedule")
            .order_by("-created_at")
        )
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)

        appt_type = self.request.query_params.get("appointment_type")
        if appt_type:
            qs = qs.filter(appointment_type__iexact=appt_type)

        return qs
