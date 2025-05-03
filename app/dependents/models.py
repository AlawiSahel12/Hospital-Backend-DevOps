"""Models for managing dependents of a guardian."""

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Dependent(models.Model):
    """
    Model representing a dependent (family member) of a guardian.
    Account creation is triggered via an invitation email provided by the guardian.
    """

    guardian = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dependents",
        help_text="The KFUPM-affiliated user acting as guardian for this dependent.",
    )
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)
    national_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique National or IQAMA ID of the dependent.",
    )
    relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text="Relationship to the guardian (e.g., Child, Spouse).",
    )
    date_of_birth = models.DateField(blank=True, null=True)
    # Direct link to the account created for the dependent.
    account = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dependent_profile",
        help_text="The User account created for the dependent, if any.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.national_id})"

    class Meta:
        ordering = ["-created_at"]  # Newest records first, maybe by name or id?
        indexes = [
            models.Index(fields=["guardian"]),
        ]
