import datetime

from django.utils import timezone

from celery import shared_task

from appointment.models import Appointment
from chat.models import ChatSession


@shared_task
def prepare_upcoming_chats():
    """
    Every minute:
      • Find all *online* appointments that will start within the next 15 min
      • Skip those that already have a ChatSession
      • Create ChatSession rows idempotently
    """
    now = timezone.localtime()
    threshold = now + datetime.timedelta(minutes=15)

    # 1) fetch candidate appointments in a single, index-friendly query
    appts = Appointment.objects.filter(
        appointment_type="online",
        status__in=[Appointment.Status.CONFIRMED, Appointment.Status.PENDING],
        chat_session__isnull=True,  # ✨ no session yet
        date__gte=now.date(),  # today or later
    ).select_related("doctor", "patient")

    created = 0
    for appt in appts:
        # Build full start-datetime in local tz
        start_dt = datetime.datetime.combine(
            appt.date, appt.start_time, tzinfo=now.tzinfo
        )
        # If within the next 15 min, make/ensure a session
        if now <= start_dt <= threshold:
            _, is_new = ChatSession.objects.get_or_create(appointment=appt)
            if is_new:
                created += 1

    if created:
        print(f"[prepare_upcoming_chats] Created {created} sessions at {now:%F %T}")


END_GRACE = datetime.timedelta(seconds=0)  # delete immediately


@shared_task
def auto_close_and_purge():
    """
    • Delete sessions whose scheduled slot ended ≥ 2.5 × duration ago.
    • Delete sessions the doctor has manually closed.
    Runs every 5 minutes (Beat).
    """
    now = timezone.localtime()
    sessions = ChatSession.objects.select_related("appointment").only(
        "id",
        "closed_at",
        "closed_by",
        "appointment__date",
        "appointment__start_time",
        "appointment__end_time",
    )

    doomed = []
    for s in sessions:
        appt = s.appointment
        # 1) Manual close  → purge right away
        if s.closed_by_id:
            doomed.append(s.pk)
            continue

        # 2) Time-based close  → start + 2.5 × duration
        start_dt = datetime.datetime.combine(
            appt.date, appt.start_time, tzinfo=now.tzinfo
        )
        end_dt = datetime.datetime.combine(appt.date, appt.end_time, tzinfo=now.tzinfo)
        duration = end_dt - start_dt
        limit_dt = start_dt + duration * 2.5

        if now >= limit_dt:
            doomed.append(s.pk)

    if doomed:
        ChatSession.objects.filter(pk__in=doomed).delete()
