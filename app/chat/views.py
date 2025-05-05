# chats/views.py

from django.shortcuts import get_object_or_404

from rest_framework import mixins, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import ChatMessage, ChatSession
from chat.permissions import IsChatParticipant
from chat.serializers import ChatMessageSerializer


class BacklogPagination(PageNumberPagination):
    page_size = 20
    ordering = "id"  # ascending
    page_size_query_param = "page_size"  # let clients request smaller bursts


class MessageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    /api/chats/{session_id}/messages/?after=<last_id>&page=<n>
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated, IsChatParticipant]
    pagination_class = BacklogPagination

    def get_queryset(self):
        session_id = self.kwargs["session_id"]
        after = self.request.query_params.get("after")
        qs = ChatMessage.objects.filter(session_id=session_id)

        if after and after.isdigit():
            qs = qs.filter(pk__gt=int(after))

        return qs.select_related("sender").order_by("id")

    # attach ChatSession to check permission
    def get_object(self):
        session_id = self.kwargs["session_id"]
        return ChatSession.objects.get(pk=session_id)


class CloseChatAPIView(APIView):
    """
    POST /api/chats/<session_id>/close/
    Deletes the ChatSession (and its messages) immediately.
    Broadcasts a force-close event to all WebSocket consumers.
    """

    permission_classes = [IsAuthenticated, IsChatParticipant]

    def post(self, request, session_id):
        # Fetch or 404
        session = get_object_or_404(
            ChatSession.objects.select_related("appointment"), pk=session_id
        )

        # Check user is participant (doctor or patient)
        self.check_object_permissions(request, session)

        # Broadcast a forced-close event to any connected sockets
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat-{session_id}",
            {"type": "chat.force_close"},
        )

        # Delete the session row (cascades to ChatMessage)
        session.delete()

        # Return 204 — session is gone
        return Response(status=status.HTTP_204_NO_CONTENT)
