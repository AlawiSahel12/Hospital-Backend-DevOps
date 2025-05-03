"""
Delivery request models.
"""

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q

from prescriptions.models import PrescriptionRecord
from profiles.models import PatientProfile


class DeliveryRequest(models.Model):
    """
    Represents a delivery request for a patient.
    """

    DELIVERY_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("scheduled", "Scheduled"),
        ("processing", "Processing"),
        ("dispatched", "Dispatched"),
        ("in_transit", "In Transit"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("failed_attempt", "Failed Delivery Attempt"),
        ("returned_to_sender", "Returned to Sender"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
        ("on_hold", "On Hold"),
    )

    # Foreign key to patient profile
    patient = models.ForeignKey(
        PatientProfile, on_delete=models.CASCADE, related_name="delivery_requests"
    )

    # Foreign key to prescription record
    prescription = models.ForeignKey(
        PrescriptionRecord,
        on_delete=models.CASCADE,
        related_name="delivery_requests",
    )

    # Destination address
    delivery_address = models.CharField(max_length=255)

    # Delivery status
    status = models.CharField(
        max_length=50, choices=DELIVERY_STATUS_CHOICES, default="pending"
    )

    # Delivery created date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Delivery date
    delivery_date = models.DateField()

    # Delivery time
    delivery_time = models.TimeField()

    # Delivery person
    delivery_person = models.CharField(max_length=100)

    # Delivery notes
    notes = models.TextField(blank=True, null=True)

    # Delivery cost
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Delivery {self.tracking_number} for {self.patient}"


class Address(models.Model):
    """
    A shipping / delivery address that belongs to a single user.
    Exactly **one** address per user may be flagged `is_default=True`.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    city = models.CharField(max_length=120)
    area = models.CharField(max_length=120)
    building = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "-updated_at"]  # default first, then newest
        constraints = [
            # DB–level guarantee: at most ONE default per user
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="uniq_default_address_per_user",
            )
        ]

    def save(self, *args, **kwargs):
        """
        When this address is flagged as default,
        make sure all of the user's other addresses are unset
        **inside the same transaction** for consistency.
        """
        with transaction.atomic():
            if self.is_default:
                # unset previous default(s) in a single UPDATE
                Address.objects.filter(user=self.user, is_default=True).exclude(
                    pk=self.pk
                ).update(is_default=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} – {self.city}, {self.area}, {self.building}"
