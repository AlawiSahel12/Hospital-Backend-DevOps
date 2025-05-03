"""Unit tests for the Appointment API."""

from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from clinic.models import Clinic
from schedules.models import DoctorSchedule

User = get_user_model()


class AppointmentAPITests(APITestCase):
    def setUp(self):
        # Create users: one doctor and two patients.
        self.doctor = User.objects.create_user(
            email="doctor@example.com",
            first_name="Doc",
            last_name="Tor",
            password="password123",
            role="doctor",
        )
        self.patient = User.objects.create_user(
            email="patient@example.com",
            first_name="Pat",
            last_name="Ient",
            password="password123",
            role="patient",
        )
        self.other_patient = User.objects.create_user(
            email="otherpatient@example.com",
            first_name="Other",
            last_name="Patient",
            password="password123",
            role="patient",
        )

        # Create a clinic.
        self.clinic = Clinic.objects.create(name="Test Clinic")

        # Create a schedule for tomorrow from 14:00 to 15:00 with 15-minute slots.
        tomorrow = date.today() + timedelta(days=1)
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            date=tomorrow,
            start_time=time(14, 0),
            end_time=time(15, 0),
            slot_duration=15,
            is_active=True,
        )
        # Calculate valid time slots for reference.
        # Expected slots: (14:00-14:15), (14:15-14:30), (14:30-14:45), (14:45-15:00)
        self.valid_slots = self.schedule.get_time_slots()

        # Set up API clients for doctor and patient.
        self.patient_client = APIClient()
        self.patient_client.force_authenticate(user=self.patient)

        self.doctor_client = APIClient()
        self.doctor_client.force_authenticate(user=self.doctor)

        self.other_patient_client = APIClient()
        self.other_patient_client.force_authenticate(user=self.other_patient)

        # URL for appointments list and creation.
        self.appt_list_url = reverse("appointment:appointment-list")

    # Helper method to create an appointment via API.
    def create_appointment(self, client, schedule_id, start_time_str):
        data = {
            "schedule": schedule_id,
            "start_time": start_time_str,
        }
        response = client.post(self.appt_list_url, data, format="json")
        return response

    # ----- Create Appointment Tests -----

    def test_create_appointment_valid(self):
        # Use first valid slot (e.g., 14:00 - 14:15)
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        response = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient"], self.patient.id)
        self.assertEqual(response.data["doctor"], self.doctor.id)
        self.assertEqual(response.data["clinic"], self.clinic.id)
        # The end_time should match computed slot end.
        expected_end = (
            (
                datetime.combine(self.schedule.date, self.valid_slots[0][0])
                + timedelta(minutes=self.schedule.slot_duration)
            )
            .time()
            .strftime("%H:%M:%S")
        )
        self.assertEqual(response.data["end_time"], expected_end)

    def test_create_appointment_missing_schedule(self):
        response = self.patient_client.post(
            self.appt_list_url, {"start_time": "14:00:00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_missing_start_time(self):
        response = self.patient_client.post(
            self.appt_list_url, {"schedule": self.schedule.id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_appointment_invalid_time_slot(self):
        # Use an invalid start time (e.g., not matching any valid slot).
        response = self.create_appointment(
            self.patient_client, self.schedule.id, "14:05:00"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid time slot", str(response.data))

    def test_double_booking(self):
        # Create an appointment in the first slot.
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp1 = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Attempt to create another appointment in the same slot (by same patient).
        resp2 = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Selected time slot is not available.", str(resp2.data))

    # ----- Listing and Retrieval Tests -----


def test_list_appointments_patient(self):
    # Create an appointment for self.patient.
    valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
    self.create_appointment(self.patient_client, self.schedule.id, valid_start)
    # List appointments as the patient.
    response = self.patient_client.get(self.appt_list_url, format="json")
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    for appt in response.data:
        self.assertEqual(appt["patient_name"], str(self.patient))


def test_list_appointments_doctor(self):
    # Create an appointment for the patient.
    valid_start = self.valid_slots[1][0].strftime("%H:%M:%S")
    self.create_appointment(self.patient_client, self.schedule.id, valid_start)
    # List appointments as the doctor.
    response = self.doctor_client.get(self.appt_list_url, format="json")
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    for appt in response.data:
        self.assertEqual(appt["doctor_name"], str(self.doctor))

    def test_retrieve_appointment_authorized(self):
        # Create an appointment.
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]

        # Patient retrieves the appointment.
        url = reverse("appointment:appointment-detail", kwargs={"pk": appt_id})
        response = self.patient_client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], appt_id)

    def test_retrieve_appointment_unauthorized(self):
        # Create an appointment with self.patient.
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]

        # Other patient attempts to retrieve the appointment.
        url = reverse("appointment:appointment-detail", kwargs={"pk": appt_id})
        response = self.other_patient_client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----- Cancellation Tests -----

    def test_cancel_appointment_valid(self):
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]

        cancel_url = reverse("appointment:appointment-cancel", kwargs={"pk": appt_id})
        response = self.patient_client.post(
            cancel_url, {"cancellation_reason": "Not needed"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"].lower(), "canceled")

    def test_cancel_appointment_already_canceled(self):
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]

        cancel_url = reverse("appointment:appointment-cancel", kwargs={"pk": appt_id})
        # First cancellation.
        self.patient_client.post(
            cancel_url, {"cancellation_reason": "Not needed"}, format="json"
        )
        # Second cancellation should fail.
        response = self.patient_client.post(
            cancel_url, {"cancellation_reason": "Trying again"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----- Rescheduling Tests -----

    def test_reschedule_appointment_valid(self):
        # Create an appointment that can be rescheduled.
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        orig_appt_id = resp.data["id"]

        # Create a new schedule for rescheduling (e.g., tomorrow + 1 day, same times).
        new_date = self.schedule.date + timedelta(days=1)
        new_schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            clinic=self.clinic,
            date=new_date,
            start_time=time(15, 0),
            end_time=time(16, 0),
            slot_duration=15,
            is_active=True,
        )
        new_valid_slots = new_schedule.get_time_slots()
        # Use first valid slot of the new schedule.
        new_start = new_valid_slots[0][0].strftime("%H:%M:%S")
        reschedule_url = reverse(
            "appointment:appointment-reschedule", kwargs={"pk": orig_appt_id}
        )
        response = self.patient_client.post(
            reschedule_url,
            {"new_schedule": new_schedule.id, "new_start_time": new_start},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that the original appointment's status is updated.
        self.assertEqual(response.data["original"]["status"].lower(), "rescheduled")
        # Check that a new appointment is created.
        self.assertEqual(response.data["new"]["status"].lower(), "confirmed")

    def test_reschedule_appointment_invalid_state(self):
        # Create an appointment and cancel it.
        valid_start = self.valid_slots[1][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]
        cancel_url = reverse("appointment:appointment-cancel", kwargs={"pk": appt_id})
        self.patient_client.post(
            cancel_url, {"cancellation_reason": "Not needed"}, format="json"
        )

        # Attempt to reschedule a canceled appointment.
        reschedule_url = reverse(
            "appointment:appointment-reschedule", kwargs={"pk": appt_id}
        )
        response = self.patient_client.post(
            reschedule_url,
            {"new_schedule": self.schedule.id, "new_start_time": valid_start},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reschedule_invalid_time_slot(self):
        # Create an appointment to be rescheduled.
        valid_start = self.valid_slots[2][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]

        # Attempt to reschedule with an invalid start time for the new schedule.
        reschedule_url = reverse(
            "appointment:appointment-reschedule", kwargs={"pk": appt_id}
        )
        response = self.patient_client.post(
            reschedule_url,
            {"new_schedule": self.schedule.id, "new_start_time": "14:05:00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----- Slot Availability Tests -----

    def test_booked_slot_not_available(self):
        # Book a valid slot.
        valid_start = self.valid_slots[0][0].strftime("%H:%M:%S")
        self.create_appointment(self.patient_client, self.schedule.id, valid_start)
        # Get available slots for the schedule.
        available_slots = self.schedule.get_available_time_slots()
        booked_slot = self.valid_slots[0]
        self.assertNotIn(booked_slot, available_slots)

    def test_canceled_appointment_slot_available(self):
        # Book and then cancel an appointment.
        valid_start = self.valid_slots[1][0].strftime("%H:%M:%S")
        resp = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start
        )
        appt_id = resp.data["id"]
        cancel_url = reverse("appointment:appointment-cancel", kwargs={"pk": appt_id})
        self.patient_client.post(
            cancel_url, {"cancellation_reason": "Not needed"}, format="json"
        )
        # Check that the slot is now available.
        available_slots = self.schedule.get_available_time_slots()
        self.assertIn(self.valid_slots[1], available_slots)

    def test_reschedule_conflict(self):
        # Create two appointments for two different patients in different slots.
        valid_start1 = self.valid_slots[0][0].strftime("%H:%M:%S")
        valid_start2 = self.valid_slots[1][0].strftime("%H:%M:%S")
        resp1 = self.create_appointment(
            self.patient_client, self.schedule.id, valid_start1
        )
        resp2 = self.create_appointment(  # noqa
            self.other_patient_client, self.schedule.id, valid_start2
        )
        # Attempt to reschedule the first appointment into the slot already booked by the other patient.
        appt_id = resp1.data["id"]
        reschedule_url = reverse(
            "appointment:appointment-reschedule", kwargs={"pk": appt_id}
        )
        response = self.patient_client.post(
            reschedule_url,
            {"new_schedule": self.schedule.id, "new_start_time": valid_start2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Selected time slot is not available", str(response.data))
