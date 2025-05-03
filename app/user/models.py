"""
User models.
"""

import re

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError("User must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create and return a new superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    ROLE_PATIENT = "patient"
    ROLE_DOCTOR = "doctor"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = (
        (ROLE_PATIENT, "Patient"),
        (ROLE_DOCTOR, "Doctor"),
        (ROLE_ADMIN, "Admin"),
    )
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=ROLE_PATIENT,
        editable=False,  # Prevent direct edits via forms
    )

    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255)

    # Optional Arabic name fields
    first_name_ar = models.CharField(max_length=255, blank=True, null=True)
    middle_name_ar = models.CharField(max_length=255, blank=True, null=True)
    last_name_ar = models.CharField(max_length=255, blank=True, null=True)

    national_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text="National or IQAMA ID",
    )
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    @property
    def is_student(self):
        local_part = self.email.split("@")[0]  # Extract part before @
        return re.match(r"^[sSgG]\d{9}$", local_part) is not None

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        """Return the full name of the user."""
        full_name = f"{self.first_name} "
        if self.middle_name:
            full_name += f"{self.middle_name} "
        full_name += self.last_name
        return full_name
