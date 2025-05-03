# tasks.py
"""
Celery tasks for processing dependent invitations.

This task wraps the transactional invitation processing logic from services.py.
It is triggered only after pre‑Celery validations have succeeded.
"""

import logging

from celery import shared_task

from .services import apply_dependent_invitation

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=30,
    retry_kwargs={"max_retries": 3},
    name="dependents.process_invitation",
)
def process_dependent_invitation_task(
    self, guardian_id, dependent_id, invitation_email
):
    """
    Celery task to perform the invitation process.

    Args:
        guardian_id (int): ID of the guardian.
        dependent_id (int): ID of the dependent.
        invitation_email (str): The original invitation email.

    Returns:
        dict: Result indicating the outcome (e.g., "password_reset_sent" or "account_created").
    """
    task_id = self.request.id
    logger.info(
        "[Task %s] Processing invitation: guardian=%s, dependent=%s, email=%s",
        task_id,
        guardian_id,
        dependent_id,
        invitation_email,
    )
    try:
        result = apply_dependent_invitation(guardian_id, dependent_id, invitation_email)
        logger.info("[Task %s] Invitation processed: %s", task_id, result)
        return result
    except Exception as exc:
        logger.error("[Task %s] Error: %s", task_id, exc)
        raise self.retry(exc=exc)
