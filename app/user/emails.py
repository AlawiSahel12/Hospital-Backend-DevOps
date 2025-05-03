import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_user_password_reset_email(user, recipient_email, uid, token):
    """
    Sends a password reset email to the user.

    Args:
        user: The user instance requesting a password reset.
        recipient_email (str): The target email address.
        uid (str): The URL-safe base64 encoded user ID.
        token (str): The password reset token.
    """
    context = {
        "first_name": user.first_name,
        "reset_link": f"{settings.FRONTEND_URL}/reset-password/confirm/?uid={uid}&token={token}",
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
