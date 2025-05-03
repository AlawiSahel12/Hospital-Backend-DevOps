"""
Lightweight JWT authentication for Django Channels.
Works with DRF SimpleJWT tokens passed as:
  • ?token=<JWT>      (query string)   OR
  • Authorization: Bearer <JWT>        (header)
"""

from urllib.parse import parse_qs

from django.contrib.auth import get_user_model

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()
jwt_auth = JWTAuthentication()


@database_sync_to_async
def get_user(validated_token):
    try:
        user = jwt_auth.get_user(validated_token)
        return user if user.is_active else None
    except Exception:
        return None


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope.get("headers", []))
        token = None

        # 1) Authorization header
        auth_header = headers.get(b"authorization", b"").decode()
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", maxsplit=1)[1]

        # 2) ?token= query string
        if not token:
            query_string = scope.get("query_string", b"").decode()
            token = parse_qs(query_string).get("token", [None])[0]

        if token:
            try:
                validated = jwt_auth.get_validated_token(token)
                scope["user"] = await get_user(validated)
            except Exception:
                scope["user"] = None
        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)
