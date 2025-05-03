from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import ChatMessage, ChatSession
from chat.serializers import ChatMessageSerializer


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket endpoint:
        wss://<host>/ws/chat/<session_id>/?token=<JWT>
    """

    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.user = self.scope.get("user")

        # ─── Guard clauses ────────────────────────────────────────────────
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)  # unauthenticated
            return

        try:
            self.session = await self.get_session()
        except ChatSession.DoesNotExist:
            await self.close(code=4004)  # not found
            return

        if not await self.is_participant():
            await self.close(code=4003)  # forbidden
            return

        # ─── Accept and join group ────────────────────────────────────────
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    # ------------------------------------------------------------------ #

    async def receive_json(self, content, **kwargs):
        body = content.get("body", "").strip()
        if not body:
            return
        msg = await self.save_message(body=body)
        payload = ChatMessageSerializer(msg).data

        await self.channel_layer.group_send(
            self.group_name, {"type": "chat.message", "payload": payload}
        )

    async def chat_message(self, event):
        await self.send_json(event["payload"])

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_force_close(self, event):
        """
        Called when the REST endpoint broadcasts a forced close.
        """
        await self.close(code=4000)  # custom code; client treats as 'ended'

    # ─── Helpers (DB access in threads) ──────────────────────────────── #

    @property
    def group_name(self):
        return f"chat-{self.session_id}"

    # database_sync_to_async wrappers
    from asgiref.sync import sync_to_async as _dsa

    @_dsa
    def get_session(self):
        return ChatSession.objects.select_related(
            "appointment__doctor", "appointment__patient"
        ).get(pk=self.session_id)

    @_dsa
    def is_participant(self):
        a = self.session.appointment
        return self.user.pk in (a.doctor_id, a.patient_id)

    @_dsa
    def save_message(self, body: str):
        return ChatMessage.objects.create(
            session=self.session,
            sender=self.user,
            body=body,
        )
