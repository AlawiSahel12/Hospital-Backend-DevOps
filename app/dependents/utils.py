"""
Utility functions for dependents app
This module provides functions to generate secure tokens and unique identifiers
for password reset and user identification.
"""

import hashlib

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def generate_password_reset_token(user):
    """Generate secure token with timestamp validation"""
    return PasswordResetTokenGenerator().make_token(user)


def generate_secure_uid(user):
    """Create non-predictable user ID encoding"""
    return urlsafe_base64_encode(
        hashlib.sha256(force_bytes(user.pk)).digest()  # Fixed missing )
    )
