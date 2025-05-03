import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# app.conf.task_routes = {
#     "dependents.tasks.process_dependent_invitation_task": {"queue": "invitations"},
#     "dependents.tasks.send_*": {"queue": "emails"},
#     "user.send_password_reset_email_task": {"queue": "emails"},
# }


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


CELERY_BEAT_SCHEDULE = {
    "prepare-upcoming-chats": {
        "task": "chat.tasks.prepare_upcoming_chats",
        "schedule": 60.0,  # every minute
    },
    "close-and-purge-chats": {
        "task": "chat.tasks.auto_close_and_purge",
        "schedule": 60.0,
    },
}
