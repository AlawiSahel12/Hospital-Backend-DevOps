# """
# Test cases for Doctor Schedules in the hospital appointment booking system.
# """

# import datetime

# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse

# from rest_framework import status
# from rest_framework.test import APIClient

# from appointment.models import DoctorSchedule
# from appointment.serializers import DoctorScheduleSerializer
# from clinic.models import Clinic
# from profiles.models import DoctorProfile

# User = get_user_model()


# class DoctorScheduleViewSetTests(TestCase):
#     """
#     Test the DoctorSchedule ViewSet API endpoints.
#     """

#     def setUp(self):
#         """
#         Set up test data.
#         """
#         # Create admin user
#         self.admin_user = User.objects.create_user(
#             email="admin@example.com", password="adminpass123", is_staff=True
#         )

#         # Create regular user
#         self.regular_user = User.objects.create_user(
#             email="user@example.com", password="userpass123", is_staff=False
#         )

#         # Create doctor user
#         self.doctor_user = User.objects.create_user(
#             email="doctor@example.com", password="doctorpass123", is_staff=False
#         )

#         # Create doctor profile for the doctor user
#         self.doctor_profile = DoctorProfile.objects.create(
#             user=self.doctor_user,
#             specialization="General Medicine",
#             experience_years=5,
#             is_active=True,
#         )

#         # Create a clinic
#         self.clinic = Clinic.objects.create(
#             name="Main Hospital",
#             slug="main-hospital",
#             address="123 Health St",
#             city="Medville",
#             state="MD",
#             zip_code="12345",
#             phone="555-123-4567",
#             is_active=True,
#         )

#         # Create a second clinic for testing
#         self.clinic2 = Clinic.objects.create(
#             name="Dental Clinic",
#             slug="dental-clinic",
#             address="456 Tooth Ave",
#             city="Medville",
#             state="MD",
#             zip_code="12345",
#             phone="555-987-6543",
#             is_active=True,
#         )

#         # Set up dates for testing
#         self.today = datetime.date.today()
#         self.tomorrow = self.today + datetime.timedelta(days=1)
#         self.yesterday = self.today - datetime.timedelta(days=1)

#         # Create a doctor schedule
#         self.schedule = DoctorSchedule.objects.create(
#             doctor=self.doctor_user,
#             clinic=self.clinic,
#             date=self.tomorrow,
#             start_time=datetime.time(9, 0),  # 9:00 AM
#             end_time=datetime.time(17, 0),  # 5:00 PM
#             slot_duration=30,  # 30 minute slots
#             appointment_type="physical",
#             is_active=True,
#         )

#         # API client for making requests
#         self.client = APIClient()

#         # URLs
#         self.list_url = reverse("appointment:doctor-schedule-list")
#         self.detail_url = reverse(
#             "appointment:doctor-schedule-detail", args=[self.schedule.id]
#         )
#         self.repeated_url = reverse("appointment:doctor-schedule-repeated")

#     def test_list_doctor_schedules_unauthenticated(self):
#         """Test that unauthenticated users can list doctor schedules (read-only)"""
#         response = self.client.get(self.list_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)

#     def test_retrieve_doctor_schedule_unauthenticated(self):
#         """Test that unauthenticated users can retrieve a doctor schedule"""
#         response = self.client.get(self.detail_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["id"], self.schedule.id)

#     def test_create_doctor_schedule_unauthenticated_fails(self):
#         """Test that unauthenticated users cannot create doctor schedules"""
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "date": self.today.strftime("%Y-%m-%d"),
#             "start_time": "10:00:00",
#             "end_time": "16:00:00",
#             "slot_duration": 60,
#             "appointment_type": "online",
#             "is_active": True,
#         }
#         response = self.client.post(self.list_url, data)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_create_doctor_schedule_non_staff_fails(self):
#         """Test that non-staff users cannot create doctor schedules"""
#         self.client.force_authenticate(user=self.regular_user)

#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "date": self.today.strftime("%Y-%m-%d"),
#             "start_time": "10:00:00",
#             "end_time": "16:00:00",
#             "slot_duration": 60,
#             "appointment_type": "online",
#             "is_active": True,
#         }
#         response = self.client.post(self.list_url, data)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_create_doctor_schedule_staff_succeeds(self):
#         """Test that staff users can create doctor schedules"""
#         self.client.force_authenticate(user=self.admin_user)

#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "date": self.today.strftime("%Y-%m-%d"),
#             "start_time": "10:00:00",
#             "end_time": "16:00:00",
#             "slot_duration": 60,
#             "appointment_type": "online",
#             "is_active": True,
#         }
#         response = self.client.post(self.list_url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(DoctorSchedule.objects.count(), 2)

#         new_schedule = DoctorSchedule.objects.get(id=response.data["id"])
#         self.assertEqual(new_schedule.doctor, self.doctor_user)
#         self.assertEqual(new_schedule.clinic, self.clinic)
#         self.assertEqual(new_schedule.appointment_type, "online")

#     def test_update_doctor_schedule_staff_succeeds(self):
#         """Test that staff users can update doctor schedules"""
#         self.client.force_authenticate(user=self.admin_user)

#         data = {
#             "start_time": "10:00:00",
#             "end_time": "18:00:00",
#             "slot_duration": 45,
#         }
#         response = self.client.patch(self.detail_url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         updated_schedule = DoctorSchedule.objects.get(id=self.schedule.id)
#         self.assertEqual(updated_schedule.start_time, datetime.time(10, 0))
#         self.assertEqual(updated_schedule.end_time, datetime.time(18, 0))
#         self.assertEqual(updated_schedule.slot_duration, 45)

#     def test_update_doctor_schedule_non_staff_fails(self):
#         """Test that non-staff users cannot update doctor schedules"""
#         self.client.force_authenticate(user=self.regular_user)

#         data = {
#             "start_time": "10:00:00",
#             "end_time": "18:00:00",
#         }
#         response = self.client.patch(self.detail_url, data)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_invalid_schedule_time_range(self):
#         """Test validation error when end_time <= start_time"""
#         self.client.force_authenticate(user=self.admin_user)

#         # Test case where end_time equals start_time
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "date": self.today.strftime("%Y-%m-%d"),
#             "start_time": "10:00:00",
#             "end_time": "10:00:00",
#             "slot_duration": 30,
#             "appointment_type": "physical",
#             "is_active": True,
#         }
#         response = self.client.post(self.list_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Test case where end_time is before start_time
#         data["end_time"] = "09:00:00"
#         response = self.client.post(self.list_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# class RepeatedDoctorScheduleTests(TestCase):
#     """
#     Test the functionality for creating repeated doctor schedules.
#     """

#     def setUp(self):
#         """
#         Set up test data.
#         """
#         # Create admin user
#         self.admin_user = User.objects.create_user(
#             email="admin@example.com", password="adminpass123", is_staff=True
#         )

#         # Create doctor user
#         self.doctor_user = User.objects.create_user(
#             email="doctor@example.com", password="doctorpass123", is_staff=False
#         )

#         # Create doctor profile for the doctor user
#         self.doctor_profile = DoctorProfile.objects.create(
#             user=self.doctor_user,
#             specialization="General Medicine",
#             experience_years=5,
#             is_active=True,
#         )

#         # Create a clinic
#         self.clinic = Clinic.objects.create(
#             name="Main Hospital",
#             slug="main-hospital",
#             address="123 Health St",
#             city="Medville",
#             state="MD",
#             zip_code="12345",
#             phone="555-123-4567",
#             is_active=True,
#         )

#         # Set up dates for testing
#         self.today = datetime.date.today()
#         self.next_month = self.today + datetime.timedelta(days=30)

#         # API client for making requests
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.admin_user)

#         # URL for repeated schedules endpoint
#         self.repeated_url = reverse("appointment:doctor-schedule-repeated")

#     def test_create_repeated_schedules(self):
#         """Test creating repeated schedules on specified weekdays"""
#         start_date = self.today
#         end_date = self.next_month

#         # Create schedules for Mondays and Wednesdays
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "start_date": start_date.strftime("%Y-%m-%d"),
#             "end_date": end_date.strftime("%Y-%m-%d"),
#             "weekdays": ["M", "W"],  # Monday and Wednesday
#             "start_time": "09:00:00",
#             "end_time": "17:00:00",
#             "slot_duration": 30,
#             "appointment_type": "physical",
#         }

#         response = self.client.post(self.repeated_url, data)
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         # Count expected number of Mondays and Wednesdays in date range
#         expected_count = 0
#         current_date = start_date
#         while current_date <= end_date:
#             if (
#                 current_date.weekday() == 0 or current_date.weekday() == 2
#             ):  # Monday or Wednesday
#                 expected_count += 1
#             current_date += datetime.timedelta(days=1)

#         # Check that the correct number of schedules were created
#         self.assertEqual(len(response.data), expected_count)
#         self.assertEqual(DoctorSchedule.objects.count(), expected_count)

#         # Verify the first schedule details
#         first_schedule = DoctorSchedule.objects.order_by("date").first()
#         self.assertEqual(first_schedule.doctor, self.doctor_user)
#         self.assertEqual(first_schedule.clinic, self.clinic)
#         self.assertEqual(first_schedule.start_time, datetime.time(9, 0))
#         self.assertEqual(first_schedule.end_time, datetime.time(17, 0))
#         self.assertEqual(first_schedule.slot_duration, 30)
#         self.assertEqual(first_schedule.appointment_type, "physical")

#     def test_repeated_schedules_with_invalid_date_range(self):
#         """Test validation when end_date is before start_date"""
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "start_date": self.next_month.strftime("%Y-%m-%d"),
#             "end_date": self.today.strftime("%Y-%m-%d"),  # Before start_date
#             "weekdays": ["M", "W"],
#             "start_time": "09:00:00",
#             "end_time": "17:00:00",
#             "slot_duration": 30,
#             "appointment_type": "physical",
#         }

#         response = self.client.post(self.repeated_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_repeated_schedules_with_invalid_time_range(self):
#         """Test validation when end_time <= start_time"""
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "start_date": self.today.strftime("%Y-%m-%d"),
#             "end_date": self.next_month.strftime("%Y-%m-%d"),
#             "weekdays": ["T", "R"],  # Tuesday and Thursday
#             "start_time": "17:00:00",
#             "end_time": "09:00:00",  # Before start_time
#             "slot_duration": 30,
#             "appointment_type": "physical",
#         }

#         response = self.client.post(self.repeated_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_repeated_schedules_with_invalid_weekday(self):
#         """Test validation with invalid weekday codes"""
#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "start_date": self.today.strftime("%Y-%m-%d"),
#             "end_date": self.next_month.strftime("%Y-%m-%d"),
#             "weekdays": ["X", "Y"],  # Invalid weekday codes
#             "start_time": "09:00:00",
#             "end_time": "17:00:00",
#             "slot_duration": 30,
#             "appointment_type": "physical",
#         }

#         response = self.client.post(self.repeated_url, data)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_non_staff_user_cannot_create_repeated_schedules(self):
#         """Test that non-staff users cannot create repeated schedules"""
#         # Create regular user and authenticate
#         regular_user = User.objects.create_user(
#             email="user@example.com", password="userpass123", is_staff=False
#         )
#         self.client.force_authenticate(user=regular_user)

#         data = {
#             "doctor": self.doctor_user.id,
#             "clinic": self.clinic.id,
#             "start_date": self.today.strftime("%Y-%m-%d"),
#             "end_date": self.next_month.strftime("%Y-%m-%d"),
#             "weekdays": ["M", "W"],
#             "start_time": "09:00:00",
#             "end_time": "17:00:00",
#             "slot_duration": 30,
#             "appointment_type": "physical",
#         }

#         response = self.client.post(self.repeated_url, data)
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class DoctorScheduleMethodTests(TestCase):
#     """
#     Test the model methods and helper functions for DoctorSchedule.
#     """

#     def setUp(self):
#         """
#         Set up test data.
#         """
#         # Create doctor user
#         self.doctor_user = User.objects.create_user(
#             email="doctor@example.com", password="doctorpass123", is_staff=False
#         )

#         # Create doctor profile
#         self.doctor_profile = DoctorProfile.objects.create(
#             user=self.doctor_user,
#             specialization="General Medicine",
#             experience_years=5,
#             is_active=True,
#         )

#         # Create a clinic
#         self.clinic = Clinic.objects.create(
#             name="Main Hospital",
#             slug="main-hospital",
#             address="123 Health St",
#             city="Medville",
#             state="MD",
#             zip_code="12345",
#             is_active=True,
#         )

#         # Set up dates for testing
#         self.today = datetime.date.today()

#         # Create a doctor schedule from 9am to 12pm with 30-minute slots
#         self.schedule = DoctorSchedule.objects.create(
#             doctor=self.doctor_user,
#             clinic=self.clinic,
#             date=self.today,
#             start_time=datetime.time(9, 0),  # 9:00 AM
#             end_time=datetime.time(12, 0),  # 12:00 PM
#             slot_duration=30,  # 30 minute slots
#             appointment_type="physical",
#             is_active=True,
#         )

#     def test_get_available_time_slots(self):
#         """Test that get_available_time_slots returns correct slots"""
#         time_slots = self.schedule.get_available_time_slots()

#         # Expected slots: 9:00-9:30, 9:30-10:00, 10:00-10:30, 10:30-11:00, 11:00-11:30, 11:30-12:00
#         # That's 6 slots in total for a 3-hour period with 30-minute slots
#         self.assertEqual(len(time_slots), 6)

#         # Check first slot
#         first_slot = time_slots[0]
#         self.assertEqual(first_slot[0], datetime.time(9, 0))
#         self.assertEqual(first_slot[1], datetime.time(9, 30))

#         # Check last slot
#         last_slot = time_slots[-1]
#         self.assertEqual(last_slot[0], datetime.time(11, 30))
#         self.assertEqual(last_slot[1], datetime.time(12, 0))

#     def test_time_slots_with_odd_duration(self):
#         """Test time slots with a duration that doesn't divide evenly into the schedule time"""
#         # Create a schedule from 9:00 AM to 11:00 AM with 45-minute slots
#         schedule = DoctorSchedule.objects.create(
#             doctor=self.doctor_user,
#             clinic=self.clinic,
#             date=self.today,
#             start_time=datetime.time(9, 0),  # 9:00 AM
#             end_time=datetime.time(11, 0),  # 11:00 AM
#             slot_duration=45,  # 45 minute slots
#             appointment_type="online",
#             is_active=True,
#         )

#         time_slots = schedule.get_available_time_slots()

#         # Expected slots: 9:00-9:45, 9:45-10:30, 10:30-11:00 (this last one is truncated)
#         self.assertEqual(len(time_slots), 2)  # Should be 2 full slots

#         # Check first slot
#         first_slot = time_slots[0]
#         self.assertEqual(first_slot[0], datetime.time(9, 0))
#         self.assertEqual(first_slot[1], datetime.time(9, 45))

#         # Check second slot
#         second_slot = time_slots[1]
#         self.assertEqual(second_slot[0], datetime.time(9, 45))
#         self.assertEqual(second_slot[1], datetime.time(10, 30))

#     def test_schedule_serializer_available_time_slots(self):
#         """Test that the serializer correctly formats available time slots"""
#         serializer = DoctorScheduleSerializer(self.schedule)
#         available_slots = serializer.data["available_time_slots"]

#         # Expected 6 slots
#         self.assertEqual(len(available_slots), 6)

#         # Check format of first slot
#         first_slot = available_slots[0]
#         self.assertEqual(first_slot, "09:00:00 - 09:30:00")

#         # Check format of last slot
#         last_slot = available_slots[-1]
#         self.assertEqual(last_slot, "11:30:00 - 12:00:00")


# class WeekdayFieldTests(TestCase):
#     """
#     Test the custom WeekdayField that converts between letter codes and weekday integers.
#     """

#     def setUp(self):
#         """Set up API client"""
#         self.client = APIClient()

#         # Create admin user and authenticate
#         self.admin_user = User.objects.create_user(
#             email="admin@example.com", password="adminpass123", is_staff=True
#         )
#         self.client.force_authenticate(user=self.admin_user)

#         # Create doctor user
#         self.doctor_user = User.objects.create_user(
#             email="doctor@example.com", password="doctorpass123", is_staff=False
#         )

#         # Create doctor profile
#         self.doctor_profile = DoctorProfile.objects.create(
#             user=self.doctor_user,
#             specialization="General Medicine",
#             experience_years=5,
#             is_active=True,
#         )

#         # Create a clinic
#         self.clinic = Clinic.objects.create(
#             name="Main Hospital",
#             slug="main-hospital",
#             address="123 Health St",
#             city="Medville",
#             state="MD",
#             zip_code="12345",
#             is_active=True,
#         )

#         # URL for repeated schedules endpoint
#         self.repeated_url = reverse("appointment:doctor-schedule-repeated")

#     def test_weekday_field_valid_values(self):
#         """Test that all valid weekday codes are accepted"""
#         # Test each valid weekday code: M, T, W, R, F, S, U
#         valid_weekdays = ["M", "T", "W", "R", "F", "S", "U"]

#         for weekday in valid_weekdays:
#             data = {
#                 "doctor": self.doctor_user.id,
#                 "clinic": self.clinic.id,
#                 "start_date": "2025-03-01",
#                 "end_date": "2025-03-08",
#                 "weekdays": [weekday],
#                 "start_time": "09:00:00",
#                 "end_time": "17:00:00",
#                 "slot_duration": 30,
#                 "appointment_type": "physical",
#             }

#             response = self.client.post(self.repeated_url, data)
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_weekday_field_case_insensitive(self):
#         """Test that weekday codes are case-insensitive"""
#         # Test lowercase weekday codes
#         lowercase_weekdays = ["m", "t", "w", "r", "f", "s", "u"]

#         for weekday in lowercase_weekdays:
#             data = {
#                 "doctor": self.doctor_user.id,
#                 "clinic": self.clinic.id,
#                 "start_date": "2025-03-01",
#                 "end_date": "2025-03-08",
#                 "weekdays": [weekday],
#                 "start_time": "09:00:00",
#                 "end_time": "17:00:00",
#                 "slot_duration": 30,
#                 "appointment_type": "physical",
#             }

#             response = self.client.post(self.repeated_url, data)
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#     def test_weekday_field_invalid_values(self):
#         """Test that invalid weekday codes are rejected"""
#         invalid_weekdays = ["A", "B", "C", "X", "Y", "Z", "1", "7"]

#         for weekday in invalid_weekdays:
#             data = {
#                 "doctor": self.doctor_user.id,
#                 "clinic": self.clinic.id,
#                 "start_date": "2025-03-01",
#                 "end_date": "2025-03-08",
#                 "weekdays": [weekday],
#                 "start_time": "09:00:00",
#                 "end_time": "17:00:00",
#                 "slot_duration": 30,
#                 "appointment_type": "physical",
#             }

#             response = self.client.post(self.repeated_url, data)
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
