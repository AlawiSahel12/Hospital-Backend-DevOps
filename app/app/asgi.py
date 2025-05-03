import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# This line WILL call django.setup() under the hood,
# so all your apps and models become available after here.
from django.core.asgi import get_asgi_application  # noqa

django_asgi_app = get_asgi_application()

from django.urls import path  # noqa

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa

from chat.consumers import ChatConsumer  # noqa

# Now it’s safe to import anything that hits models or settings
from chat.middleware import JWTAuthMiddleware  # noqa

websocket_urlpatterns = [
    path("ws/chat/<int:session_id>/", ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # HTTP goes through the standard Django ASGI app
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
