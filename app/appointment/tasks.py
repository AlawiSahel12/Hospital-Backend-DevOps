# appointment/tasks.py

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from celery import shared_task

from .models import Appointment


@shared_task
def auto_complete_old_appointments():
    """
    Find any Appointment in PENDING or CONFIRMED state whose slot is in the past,
    and mark it COMPLETED in a single atomic transaction.
    """
    now = timezone.localtime()
    today = now.date()
    current_time = now.time()

    # Build a queryset of appointments whose date is before today,
    # or whose date is today but end_time has already passed.
    to_complete = Appointment.objects.filter(
        status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
    ).filter(Q(date__lt=today) | Q(date=today, end_time__lte=current_time))

    count = 0
    with transaction.atomic():
        # Iterate so that save() hooks / signals still fire if you have any.
        for appt in to_complete.select_for_update():
            appt.status = Appointment.Status.COMPLETED
            appt.save(update_fields=["status"])
            count += 1

    return f"Auto-completed {count} appointments."
