"""
URL mappings for the delivery API.
"""

from django.urls import include, path

from rest_framework.routers import DefaultRouter

from delivery import views
from delivery.views import AddressViewSet

app_name = "delivery"

router = DefaultRouter()
router.register(r"", AddressViewSet, basename="address")


urlpatterns = [
    path("addresses/", include(router.urls)),
    path("", views.ListDeliveryView.as_view(), name="list"),
    path("create/", views.CreateDeliveryView.as_view(), name="create"),
    path("manage/<int:id>/", views.ManageDeliveryView.as_view(), name="update"),
]
