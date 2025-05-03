# import datetime
# from unittest.mock import patch

# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse

# from rest_framework import status
# from rest_framework.test import APIClient

# from appointment.models import Appointment, DoctorSchedule
# from clinic.models import Clinic
# from profiles.models import DoctorProfile

# User = get_user_model()


# class ClinicByAppointmentTypeListViewTests(TestCase):
#     """
#     Test cases for the endpoint that lists clinics by appointment type.
#     GET /appointment/clinics/?type=<physical|online>
#     """

#     def setUp(self):
#         # Create test client
#         self.client = APIClient()

#         # Create test clinics
#         self.clinic1 = Clinic.objects.create(
#             name="General Hospital",
#             address="123 Main St",
#             phone="555-1234",
#             email="general@example.com",
#             slug="general",
#         )
#         self.clinic2 = Clinic.objects.create(
#             name="Dental Center",
#             address="456 Oak St",
#             phone="555-5678",
#             email="dental@example.com",
#             slug="dental",
#         )
#         self.clinic3 = Clinic.objects.create(
#             name="Pediatric Clinic",
#             address="789 Pine St",
#             phone="555-9012",
#             email="peds@example.com",
#             slug="pediatric",
#         )

#         # Create test doctor users
#         self.doctor1 = User.objects.create_user(
#             username="doctor1",
#             email="doctor1@example.com",
#             password="password123",
#         )
#         self.doctor2 = User.objects.create_user(
#             username="doctor2",
#             email="doctor2@example.com",
#             password="password123",
#         )

#         # Create doctor profiles
#         self.doctor1_profile = DoctorProfile.objects.create(
#             user=self.doctor1,
#             specialty="General Medicine",
#             license_number="ABC123",
#             is_active=True,
#         )
#         self.doctor2_profile = DoctorProfile.objects.create(
#             user=self.doctor2,
#             specialty="Dentistry",
#             license_number="DEF456",
#             is_active=True,
#         )

#         # Create doctor schedules
#         # Clinic 1 has physical appointments only
#         self.schedule1 = DoctorSchedule.objects.create(
#             doctor=self.doctor1,
#             clinic=self.clinic1,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="physical",
#             is_active=True,
#         )

#         # Clinic 2 has both physical and online
#         self.schedule2 = DoctorSchedule.objects.create(
#             doctor=self.doctor2,
#             clinic=self.clinic2,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="physical",
#             is_active=True,
#         )
#         self.schedule3 = DoctorSchedule.objects.create(
#             doctor=self.doctor2,
#             clinic=self.clinic2,
#             date=datetime.date.today() + datetime.timedelta(days=2),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="online",
#             is_active=True,
#         )

#         # Clinic 3 has no active schedules (just an inactive one)
#         self.schedule4 = DoctorSchedule.objects.create(
#             doctor=self.doctor1,
#             clinic=self.clinic3,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="online",
#             is_active=False,  # Inactive!
#         )

#     def test_get_physical_clinics(self):
#         """Test retrieving clinics that offer physical appointments."""
#         url = f"{reverse('appointment:clinics-by-type')}?type=physical"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Should include clinic1 and clinic2 (both have physical appointments)
#         self.assertEqual(len(response.data), 2)
#         clinic_slugs = [clinic["slug"] for clinic in response.data]
#         self.assertIn(self.clinic1.slug, clinic_slugs)
#         self.assertIn(self.clinic2.slug, clinic_slugs)
#         self.assertNotIn(self.clinic3.slug, clinic_slugs)

#     def test_get_online_clinics(self):
#         """Test retrieving clinics that offer online appointments."""
#         url = f"{reverse('appointment:clinics-by-type')}?type=online"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Should include only clinic2 (only one with active online appointments)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["slug"], self.clinic2.slug)

#     def test_get_clinics_missing_type_param(self):
#         """Test that missing type parameter returns a validation error."""
#         url = reverse("appointment:clinics-by-type")
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_clinics_invalid_type_param(self):
#         """Test that invalid type parameter returns a validation error."""
#         url = f"{reverse('appointment:clinics-by-type')}?type=invalid"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class DoctorByClinicAndTypeListViewTests(TestCase):
#     """
#     Test cases for the endpoint that lists doctors by clinic and appointment type.
#     GET /appointment/doctors/?clinic_slug=<slug>&type=<physical|online>
#     """

#     def setUp(self):
#         # Create test client
#         self.client = APIClient()

#         # Create test clinic
#         self.clinic = Clinic.objects.create(
#             name="General Hospital",
#             address="123 Main St",
#             phone="555-1234",
#             email="general@example.com",
#             slug="general",
#         )

#         # Create test doctor users
#         self.doctor1 = User.objects.create_user(
#             username="doctor1",
#             email="doctor1@example.com",
#             password="password123",
#         )
#         self.doctor2 = User.objects.create_user(
#             username="doctor2",
#             email="doctor2@example.com",
#             password="password123",
#         )
#         self.doctor3 = User.objects.create_user(
#             username="doctor3",
#             email="doctor3@example.com",
#             password="password123",
#         )

#         # Create doctor profiles
#         self.doctor1_profile = DoctorProfile.objects.create(
#             user=self.doctor1,
#             specialty="General Medicine",
#             license_number="ABC123",
#             is_active=True,
#         )
#         self.doctor2_profile = DoctorProfile.objects.create(
#             user=self.doctor2,
#             specialty="Cardiology",
#             license_number="DEF456",
#             is_active=True,
#         )
#         self.doctor3_profile = DoctorProfile.objects.create(
#             user=self.doctor3,
#             specialty="Neurology",
#             license_number="GHI789",
#             is_active=True,
#         )

#         # Create doctor schedules
#         # Doctor 1 has physical appointments only
#         self.schedule1 = DoctorSchedule.objects.create(
#             doctor=self.doctor1,
#             clinic=self.clinic,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="physical",
#             is_active=True,
#         )

#         # Doctor 2 has both physical and online
#         self.schedule2 = DoctorSchedule.objects.create(
#             doctor=self.doctor2,
#             clinic=self.clinic,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="physical",
#             is_active=True,
#         )
#         self.schedule3 = DoctorSchedule.objects.create(
#             doctor=self.doctor2,
#             clinic=self.clinic,
#             date=datetime.date.today() + datetime.timedelta(days=2),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="online",
#             is_active=True,
#         )

#         # Doctor 3 has only inactive schedule
#         self.schedule4 = DoctorSchedule.objects.create(
#             doctor=self.doctor3,
#             clinic=self.clinic,
#             date=datetime.date.today() + datetime.timedelta(days=1),
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(17, 0),
#             slot_duration=30,
#             appointment_type="online",
#             is_active=False,  # Inactive!
#         )

#     def test_get_doctors_for_clinic_physical(self):
#         """Test retrieving doctors for a clinic that offer physical appointments."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?clinic_slug={self.clinic.slug}&type=physical"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Should include doctor1 and doctor2 (both have physical appointments)
#         self.assertEqual(len(response.data), 2)
#         doctor_ids = [doc["user"] for doc in response.data]
#         self.assertIn(self.doctor1.id, doctor_ids)
#         self.assertIn(self.doctor2.id, doctor_ids)
#         self.assertNotIn(self.doctor3.id, doctor_ids)

#     def test_get_doctors_for_clinic_online(self):
#         """Test retrieving doctors for a clinic that offer online appointments."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?clinic_slug={self.clinic.slug}&type=online"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Should include only doctor2 (only one with active online appointments)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["user"], self.doctor2.id)

#     def test_get_doctors_missing_clinic_param(self):
#         """Test that missing clinic parameter returns a validation error."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?type=physical"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_doctors_missing_type_param(self):
#         """Test that missing type parameter returns a validation error."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?clinic_slug={self.clinic.slug}"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_doctors_invalid_type_param(self):
#         """Test that invalid type parameter returns a validation error."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?clinic_slug={self.clinic.slug}&type=invalid"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_doctors_nonexistent_clinic(self):
#         """Test that a 404 is returned for a nonexistent clinic."""
#         url = f"{reverse('appointment:doctors-by-clinic-type')}?clinic_slug=nonexistent&type=physical"
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# class AvailableTimeSlotsViewTests(TestCase):
#     """
#     Test cases for the endpoint that lists available time slots.
#     GET /appointment/timeslots/?doctor_id=<id>&clinic_slug=<slug>&type=<physical|online>&date=<YYYY-MM-DD>
#     """

#     def setUp(self):
#         # Create test client
#         self.client = APIClient()

#         # Create test clinic
#         self.clinic = Clinic.objects.create(
#             name="General Hospital",
#             address="123 Main St",
#             phone="555-1234",
#             email="general@example.com",
#             slug="general",
#         )

#         # Create test doctor user
#         self.doctor = User.objects.create_user(
#             username="doctor1",
#             email="doctor1@example.com",
#             password="password123",
#         )

#         # Create test patient user
#         self.patient = User.objects.create_user(
#             username="patient1",
#             email="patient1@example.com",
#             password="password123",
#         )

#         # Create doctor profile
#         self.doctor_profile = DoctorProfile.objects.create(
#             user=self.doctor,
#             specialty="General Medicine",
#             license_number="ABC123",
#             is_active=True,
#         )

#         # Test date
#         self.test_date = datetime.date.today() + datetime.timedelta(days=1)

#         # Create doctor schedule
#         self.schedule = DoctorSchedule.objects.create(
#             doctor=self.doctor,
#             clinic=self.clinic,
#             date=self.test_date,
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(11, 0),
#             slot_duration=30,  # 30 min slots
#             appointment_type="physical",
#             is_active=True,
#         )

#         # Mock the get_available_time_slots method
#         self.mock_available_slots = [
#             (datetime.time(9, 0), datetime.time(9, 30)),
#             (datetime.time(9, 30), datetime.time(10, 0)),
#             (datetime.time(10, 0), datetime.time(10, 30)),
#             (datetime.time(10, 30), datetime.time(11, 0)),
#         ]

#     def test_get_available_timeslots(self):
#         """Test retrieving available time slots."""
#         with patch(
#             "appointment.models.DoctorSchedule.get_available_time_slots"
#         ) as mock_get_slots:
#             # Configure the mock to return our predefined slots
#             mock_get_slots.return_value = self.mock_available_slots

#             url = (
#                 f"{reverse('appointment:available-timeslots')}"
#                 f"?doctor_id={self.doctor.id}"
#                 f"&clinic_slug={self.clinic.slug}"
#                 f"&type=physical"
#                 f"&date={self.test_date.strftime('%Y-%m-%d')}"
#             )
#             response = self.client.get(url)

#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#             # Should include 4 time slots
#             self.assertEqual(len(response.data), 4)
#             self.assertEqual(response.data[0], "09:00 - 09:30")
#             self.assertEqual(response.data[1], "09:30 - 10:00")
#             self.assertEqual(response.data[2], "10:00 - 10:30")
#             self.assertEqual(response.data[3], "10:30 - 11:00")

#     def test_get_available_timeslots_with_booking(self):
#         """Test retrieving available time slots with a booked appointment."""
#         # Create a booked appointment
#         _ = Appointment.objects.create(
#             doctor=self.doctor,
#             patient=self.patient,
#             clinic=self.clinic,
#             schedule=self.schedule,
#             appointment_date=self.test_date,
#             start_time=datetime.time(9, 0),
#             end_time=datetime.time(9, 30),
#             appointment_type="physical",
#             status="confirmed",
#         )

#         # The first slot is now booked
#         modified_slots = self.mock_available_slots[1:]  # Skip the first slot

#         with patch(
#             "appointment.models.DoctorSchedule.get_available_time_slots"
#         ) as mock_get_slots:
#             # Configure the mock to return our modified slots (first one removed)
#             mock_get_slots.return_value = modified_slots

#             url = (
#                 f"{reverse('appointment:available-timeslots')}"
#                 f"?doctor_id={self.doctor.id}"
#                 f"&clinic_slug={self.clinic.slug}"
#                 f"&type=physical"
#                 f"&date={self.test_date.strftime('%Y-%m-%d')}"
#             )
#             response = self.client.get(url)

#             self.assertEqual(response.status_code, status.HTTP_200_OK)

#             # Should include 3 time slots (first one is booked)
#             self.assertEqual(len(response.data), 3)
#             self.assertEqual(response.data[0], "09:30 - 10:00")
#             self.assertEqual(response.data[1], "10:00 - 10:30")
#             self.assertEqual(response.data[2], "10:30 - 11:00")

#     def test_get_timeslots_missing_doctor_param(self):
#         """Test that missing doctor parameter returns a validation error."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?clinic_slug={self.clinic.slug}"
#             f"&type=physical"
#             f"&date={self.test_date.strftime('%Y-%m-%d')}"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_timeslots_missing_clinic_param(self):
#         """Test that missing clinic parameter returns a validation error."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&type=physical"
#             f"&date={self.test_date.strftime('%Y-%m-%d')}"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_timeslots_missing_type_param(self):
#         """Test that missing type parameter returns a validation error."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&clinic_slug={self.clinic.slug}"
#             f"&date={self.test_date.strftime('%Y-%m-%d')}"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_timeslots_missing_date_param(self):
#         """Test that missing date parameter returns a validation error."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&clinic_slug={self.clinic.slug}"
#             f"&type=physical"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_timeslots_invalid_date_format(self):
#         """Test that invalid date format returns a validation error."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&clinic_slug={self.clinic.slug}"
#             f"&type=physical"
#             f"&date=01-03-2025"  # Invalid format (should be YYYY-MM-DD)
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_get_timeslots_nonexistent_clinic(self):
#         """Test that a 404 is returned for a nonexistent clinic."""
#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&clinic_slug=nonexistent"
#             f"&type=physical"
#             f"&date={self.test_date.strftime('%Y-%m-%d')}"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_get_timeslots_no_schedules(self):
#         """Test getting timeslots when there are no schedules for the given params."""
#         # Use a different date with no schedules
#         different_date = self.test_date + datetime.timedelta(days=5)

#         url = (
#             f"{reverse('appointment:available-timeslots')}"
#             f"?doctor_id={self.doctor.id}"
#             f"&clinic_slug={self.clinic.slug}"
#             f"&type=physical"
#             f"&date={different_date.strftime('%Y-%m-%d')}"
#         )
#         response = self.client.get(url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 0)  # Empty list
