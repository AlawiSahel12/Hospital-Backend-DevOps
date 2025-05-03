from rest_framework import serializers

from chat.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.pk", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ("id", "sender_id", "body", "sent_at")
        read_only_fields = ("id", "sender_id", "sent_at")
