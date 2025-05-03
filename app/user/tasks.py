"""Asynchronous tasks for user-related operations."""

import logging

# from celery.exceptions import MaxRetriesExceededError
from django.contrib.auth import get_user_model

from celery import shared_task

from .emails import send_user_password_reset_email

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,  # enables exponential backoff
    retry_kwargs={"max_retries": 5},
    name="user.send_password_reset_email_task",
)
def send_password_reset_email_task(self, user_id, recipient_email, uid, token):
    """
    Asynchronous Celery task to send a password reset email for a user.

    Args:
        user_id (int): ID of the user requesting a password reset.
        recipient_email (str): The email address to which the reset email will be sent.
        uid (str): The URL-safe base64 encoded user ID.
        token (str): The password reset token.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("User with id %s does not exist", user_id)
        # Optionally, if the user is not found, we may stop further retries.
        return

    try:
        send_user_password_reset_email(user, recipient_email, uid, token)
        logger.info("Password reset email sent asynchronously to %s", recipient_email)
    except Exception as exc:
        logger.error(
            "Error sending password reset email to %s: %s", recipient_email, str(exc)
        )
        # The task will be retried automatically (up to max_retries) with exponential backoff.
        raise self.retry(exc=exc)
