# email.py
"""
Module for composing and sending emails using Django's templating system.
Email templates (HTML and plain text) are used so that messages are not hard-coded.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .utils import generate_password_reset_token  # Your token generation function

logger = logging.getLogger(__name__)


def send_welcome_email(user, recipient_email):
    """
    Sends a welcome email to a new dependent account.
    """
    context = {
        "first_name": user.first_name,
        "setup_link": f"{settings.FRONTEND_URL}/setup-account/{generate_password_reset_token(user)}/",
        "support_email": settings.SUPPORT_EMAIL,
        "subject": "Welcome to Hospital Management System",
    }
    subject = context["subject"]
    html_content = render_to_string("emails/welcome_email.html", context)
    text_content = render_to_string("emails/welcome_email.txt", context)

    try:
        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        logger.info("Welcome email sent to %s", recipient_email)
    except Exception as e:
        logger.error("Failed to send welcome email to %s: %s", recipient_email, str(e))
        raise


def send_password_reset_email(user, recipient_email):
    """
    Sends a password reset email to an existing dependent account.
    """
    context = {
        "first_name": user.first_name,
        "reset_link": f"{settings.FRONTEND_URL}/reset-password/{generate_password_reset_token(user)}/",
        "security_email": settings.SECURITY_EMAIL,
        "subject": "Password Reset Request",
    }
    subject = context["subject"]
    html_content = render_to_string("emails/password_reset_email.html", context)
    text_content = render_to_string("emails/password_reset_email.txt", context)

    try:
        email = EmailMultiAlternatives(
            subject, text_content, settings.DEFAULT_FROM_EMAIL, [recipient_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        logger.info("Password reset email sent to %s", recipient_email)
    except Exception as e:
        logger.error(
            "Failed to send password reset email to %s: %s", recipient_email, str(e)
        )
        raise
