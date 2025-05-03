"""
Tests for the user API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token_obtain_pair")
REFRESH_TOKEN_URL = reverse("user:token_refresh")
ME_URL = reverse("user:me")


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class UserRegistrationAPITests(TestCase):
    """Test user registration API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.base_payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "1990-01-01",
        }

    def test_create_user_success(self):
        """Test creating user with valid payload succeeds."""
        res = self.client.post(CREATE_USER_URL, self.base_payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=self.base_payload["email"])
        self.assertTrue(user.check_password(self.base_payload["password"]))
        self.assertNotIn("password", res.data)

    def test_create_user_existing_email_fails(self):
        """Test creating user with existing email fails."""
        create_user(**self.base_payload)
        res = self.client.post(CREATE_USER_URL, self.base_payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_short_password_fails(self):
        """Test password less than 5 characters fails."""
        payload = {**self.base_payload, "password": "pw"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            get_user_model().objects.filter(email=payload["email"]).exists()
        )

    def test_create_user_missing_required_field_fails(self):
        """Test missing required field returns error."""
        for field in ["email", "password", "first_name", "last_name"]:
            with self.subTest(field=field):
                payload = {**self.base_payload}
                del payload[field]
                res = self.client.post(CREATE_USER_URL, payload)
                self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_create_user_invalid_date_format_fails(self):
    #     """Test invalid date format returns error."""
    #     payload = {**self.base_payload, "date_of_birth": "01-01-1990"}
    #     res = self.client.post(CREATE_USER_URL, payload)
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TokenAPITests(TestCase):
    """Test JWT token authentication endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            date_of_birth="1990-01-01",
        )

    def test_obtain_token_valid_credentials(self):
        """Test obtaining token with valid credentials."""
        payload = {"email": "test@example.com", "password": "testpass123"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_obtain_token_invalid_credentials(self):
        """Test obtaining token with invalid credentials."""
        payload = {"email": "test@example.com", "password": "wrongpass"}
        res = self.client.post(TOKEN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", res.data)

    def test_obtain_token_missing_fields(self):
        """Test missing email or password returns error."""
        test_cases = [{"email": "test@example.com"}, {"password": "testpass123"}, {}]
        for payload in test_cases:
            with self.subTest(payload=payload):
                res = self.client.post(TOKEN_URL, payload)
                self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_refresh_token_valid(self):
        """Test refreshing token with valid refresh token."""
        # First obtain refresh token
        res = self.client.post(
            TOKEN_URL, {"email": "test@example.com", "password": "testpass123"}
        )
        refresh_token = res.data["refresh"]

        res_refresh = self.client.post(REFRESH_TOKEN_URL, {"refresh": refresh_token})
        self.assertEqual(res_refresh.status_code, status.HTTP_200_OK)
        self.assertIn("access", res_refresh.data)

    def test_refresh_token_invalid(self):
        """Test refreshing token with invalid refresh token."""
        res = self.client.post(REFRESH_TOKEN_URL, {"refresh": "invalid"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfilePublicAPITests(TestCase):
    """Test unauthenticated access to user profile API."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_profile_unauthorized(self):
        """Test authentication is required for accessing profile."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_unauthorized(self):
        """Test authentication is required for updating profile."""
        res = self.client.patch(ME_URL, {"first_name": "New"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfilePrivateAPITests(TestCase):
    """Test authenticated access to user profile API."""

    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            date_of_birth="1990-01-01",
        )
        self.client = APIClient()
        # Obtain and set JWT token
        res = self.client.post(
            TOKEN_URL, {"email": "test@example.com", "password": "testpass123"}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")

    def test_retrieve_profile_success(self):
        """Test retrieving profile for authenticated user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "date_of_birth": self.user.date_of_birth,
            },
        )

    def test_post_method_not_allowed(self):
        """Test POST method is not allowed for profile endpoint."""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile with valid data."""
        payload = {"first_name": "Updated", "password": "newpassword123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload["first_name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_email_to_existing_email_fails(self):
        """Test updating to an existing email address fails."""
        create_user(email="existing@example.com", password="testpass123")
        res = self.client.patch(ME_URL, {"email": "existing@example.com"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_profile_update(self):
        """Test partial update of user profile."""
        payload = {"last_name": "Updated"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, payload["last_name"])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_password_update_invalidates_old_credentials(self):
        """Test old password becomes invalid after password update."""
        new_password = "newpassword123"
        self.client.patch(ME_URL, {"password": new_password})

        # Test new password works
        res = self.client.post(
            TOKEN_URL, {"email": self.user.email, "password": new_password}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Test old password fails
        res = self.client.post(
            TOKEN_URL, {"email": self.user.email, "password": "testpass123"}
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
