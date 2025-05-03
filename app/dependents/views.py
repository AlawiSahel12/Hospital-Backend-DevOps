"""ViewSet for managing dependents and processing invitation requests."""

import logging

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from .models import Dependent
from .serializers import DependentSerializer
from .services import validate_dependent_invitation
from .tasks import process_dependent_invitation_task

logger = logging.getLogger(__name__)


class DependentViewSet(ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for managing dependents and processing invitation requests.
    Only dependents belonging to the authenticated guardian are accessible.

    GET: List all dependents for the authenticated guardian.
    POST to "invite" to trigger dependent invitation.

    """

    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dependent.objects.filter(guardian=self.request.user)

    @action(detail=False, methods=["post"], url_path="invite", name="Invite Dependent")
    def invite(self, request):
        """
        Endpoint to validate and process a dependent invitation.
        Synchronous validations occur first. If they pass, the invitation is enqueued.
        The response includes a detailed message regarding the action to be taken.
        """
        guardian_id = request.user.id
        dependent_id = request.data.get("dependent_id")
        invitation_email = request.data.get("email")

        # Pre-Celery synchronous validations.
        try:
            validation_result = validate_dependent_invitation(
                guardian_id, dependent_id, invitation_email
            )
        except ValidationError as e:
            return Response(
                {"detail": e.detail if hasattr(e, "detail") else str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Enqueue the asynchronous processing.
        process_dependent_invitation_task.delay(
            guardian_id, dependent_id, invitation_email
        )

        # Return a detailed message from validation_result.
        return Response(
            {
                "detail": validation_result.get(
                    "message", "Invitation accepted for processing."
                )
            },
            status=status.HTTP_202_ACCEPTED,
        )


class AdminDependentViewSet(viewsets.ModelViewSet):
    """
    Admin-only ViewSet for managing all dependents.
    This endpoint allows admin users to create, retrieve, list, and patch any dependent record.
    """

    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer
    permission_classes = [permissions.IsAdminUser]
