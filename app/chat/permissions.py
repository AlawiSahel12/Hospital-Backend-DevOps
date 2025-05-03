# chats/permissions.py
from rest_framework.permissions import BasePermission


class IsChatParticipant(BasePermission):
    """
    Allow access only to doctor or patient bound to the ChatSession.
    """

    def has_object_permission(self, request, view, obj):
        # obj is ChatSession *or* ChatMessage
        session = obj if hasattr(obj, "appointment") else obj.session
        appt = session.appointment
        return request.user.pk in (appt.patient_id, appt.doctor_id)
