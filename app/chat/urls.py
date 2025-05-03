# chats/urls.py
from django.urls import include, path

from rest_framework.routers import SimpleRouter

from chat.views import CloseChatAPIView, MessageViewSet

app_name = "chat"

router = SimpleRouter(trailing_slash=False)
router.register(
    r"(?P<session_id>\d+)/messages", MessageViewSet, basename="chat-messages"
)

urlpatterns = [
    # Close-chat route
    path("<int:session_id>/close/", CloseChatAPIView.as_view(), name="chat-close"),
    # Backlog routes
    path("", include(router.urls)),
]
