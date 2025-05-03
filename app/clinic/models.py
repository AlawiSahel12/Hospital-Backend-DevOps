"""Models for the clinic app."""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Clinic(models.Model):
    """Model for Clinic"""

    name = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(
        max_length=200,
        blank=True,
        default="",  # No nulls, empty string default
        help_text="Auto-filled with English name if not provided",
    )
    description = models.TextField(blank=True)
    # Logo field for SVG or any image URL (Adjust as needed)
    logo = models.TextField(
        blank=True,
        null=True,
        help_text="Store the SVG markup or image URL for the clinic logo.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-fill Arabic name with English name if empty"""
        if not self.name_ar.strip():  # Check for empty/whitespace
            self.name_ar = self.name
        super().save(*args, **kwargs)
