"""
URL mappings for the user API.
"""

from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user import views

app_name = "user"

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("me/", views.ManageUserView.as_view(), name="me"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Password reset endpoints:
    path(
        "reset-password/",
        views.PasswordResetRequestView.as_view(),
        name="reset_password_request",
    ),
    path(
        "reset-password/confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="reset_password_confirm",
    ),
]
