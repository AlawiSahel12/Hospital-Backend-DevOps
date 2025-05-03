from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from appointment.models import Appointment

User = get_user_model()


class ChatSession(models.Model):
    """
    One-to-one chat bound to a single *online* appointment.
    Created 15 min before start; deleted after close-&-purge Celery task.
    """

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name="chat_session",
        limit_choices_to={"appointment_type": "online"},
    )

    opened_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    closed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="closed_chat_sessions",
        help_text="If set, the doctor manually closed the chat.",
    )

    class Meta:
        indexes = [
            models.Index(fields=["opened_at"]),
            models.Index(fields=["closed_at"]),
        ]
        verbose_name = "Chat session"
        verbose_name_plural = "Chat sessions"

    def __str__(self) -> str:
        return f"ChatSession<{self.pk}> / appt {self.appointment_id}"

    # Convenience helpers -------------------------------------------------
    @property
    def is_open(self) -> bool:
        return self.opened_at is not None and self.closed_at is None

    def mark_open(self):
        self.opened_at = timezone.now()
        self.save(update_fields=["opened_at"])

    def mark_closed(self, by: User | None = None):
        self.closed_at = timezone.now()
        self.closed_by = by
        self.save(update_fields=["closed_at", "closed_by"])


class ChatMessage(models.Model):
    """
    Ephemeral message retained only for the lifetime of its session.
    """

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]
        indexes = [
            models.Index(fields=["session", "sent_at"]),
        ]

    def __str__(self):
        return f"Msg<{self.pk}> by {self.sender_id} in session {self.session_id}"
