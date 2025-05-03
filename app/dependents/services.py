# services.py
"""
Service layer for handling the dependent invitation process.

This module performs two main operations:

1. Synchronous pre‑Celery validation: This function validates that:
   - The dependent belongs to the guardian.
   - The provided email is valid given the current state:
      • If the dependent already has an account:
          - If the provided email matches that account, then a password reset should be sent.
          - Otherwise, a re‑invitation will be sent to the registered email.
      • If the dependent does not have an account:
          - The email must not already be in use by another user.

2. Transactional processing: Once validation passes, this function applies the changes
   by either triggering a password reset email or creating a new account and sending a welcome email.
"""

import logging

from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework.exceptions import ValidationError  # Use DRF's ValidationError

from .email import send_password_reset_email, send_welcome_email
from .models import Dependent

logger = logging.getLogger(__name__)
User = get_user_model()


def validate_dependent_invitation(guardian_id, dependent_id, invitation_email):
    """
    Performs synchronous validations *before* any Celery task is triggered.

    Checks (in the exact order):
      1. Ownership Check:
         - Verify that the provided dependent_id belongs to the guardian identified by guardian_id.
           (JWT guarantees the guardian's validity.)
      2. Email Conflict Check:
         - If the dependent already has a linked user account:
             • If the provided email matches the account email: return action "send_reset".
             • If it does not match: return action "send_reset_mismatch" along with a message
               indicating that a re‑invitation will be sent to the registered email.
         - If the dependent does not have an account:
             • If the provided email is not already in use: return action "create_account".
             • If the email is already registered to another user: raise a ValidationError.

    Args:
        guardian_id (int): ID of the authenticated guardian.
        dependent_id (int): ID of the dependent.
        invitation_email (str): Provided invitation email.

    Returns:
        dict: Contains:
          - "action": "send_reset", "send_reset_mismatch" or "create_account"
          - "dependent": the Dependent instance.
          - "resolved_email": email address to be used.
          - "message": Optional frontend message (e.g. for mismatches).

    Raises:
        ValidationError: If any check fails.
    """
    # No need to check guardian existence since JWT guarantees it.
    guardian = User.objects.get(id=guardian_id)  # Assumes valid from JWT context.
    try:
        dependent = Dependent.objects.get(id=dependent_id, guardian=guardian)
    except Dependent.DoesNotExist:
        raise ValidationError(
            "Dependent not found or not associated with the guardian."
        )

    invitation_email = invitation_email.strip().lower()

    if dependent.account:
        # Dependent already has an associated account.
        if invitation_email == dependent.account.email.lower():
            # Case 1: Provided email matches the registered account.
            return {
                "action": "send_reset",
                "dependent": dependent,
                "resolved_email": invitation_email,
                "message": "Invitation accepted. A password reset email will be sent to your registered email.",
            }
        else:
            # Case 2: Provided email does NOT match the registered account.
            return {
                "action": "send_reset_mismatch",
                "dependent": dependent,
                "resolved_email": dependent.account.email,
                "message": f"This dependent already has an account with email {
                    dependent.account.email}. A re-invitation has been sent to that address.",
            }
    else:
        # Dependent does not have an account.
        if User.objects.filter(email=invitation_email).exists():
            raise ValidationError(
                "This email is already registered to another user. Please provide a different email address."
            )
        return {
            "action": "create_account",
            "dependent": dependent,
            "resolved_email": invitation_email,
            "message": "Invitation accepted. An account creation email will be sent.",
        }


def apply_dependent_invitation(guardian_id, dependent_id, invitation_email):
    """
    Processes the invitation transactionally.

    Based on the result from validate_dependent_invitation:
      - If the dependent already has an account (either "send_reset" or "send_reset_mismatch"):
          • Send a password reset email to the registered address.
      - Otherwise ("create_account"):
          • Create a new user account, link it to the dependent, and send a welcome email.

    Returns:
        dict: {"status": "password_reset_sent"} or {"status": "account_created"}
    """
    with transaction.atomic():
        guardian = User.objects.get(id=guardian_id)
        dependent = Dependent.objects.select_for_update().get(
            id=dependent_id, guardian=guardian
        )

        if dependent.account:
            # For both "send_reset" and "send_reset_mismatch", use the registered account email.
            send_password_reset_email(dependent.account, dependent.account.email)
            status = "password_reset_sent"
        else:
            new_user = User.objects.create_user(
                email=invitation_email,
                first_name=dependent.first_name,
                last_name=dependent.last_name,
                is_active=True,
            )
            dependent.account = new_user
            dependent.save(update_fields=["account"])
            send_welcome_email(new_user, invitation_email)
            status = "account_created"

    logger.info(
        "Invitation applied for dependent id %s with status %s", dependent_id, status
    )
    return {"status": status}
