"""
Tests for the Django admin modifications.
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Create user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            # date_of_birth is optional
        )

    def test_users_lists(self):
        """Test that users are listed on page."""
        url = reverse("admin:user_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, str(self.user))
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse("admin:user_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse("admin:user_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
