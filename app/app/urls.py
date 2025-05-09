"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health-check/", core_views.health_check, name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/user/", include("user.urls")),
    path("api/records/", include("records.urls")),
    path("api/appointment/", include("appointment.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/clinic/", include("clinic.urls")),
    path("api/schedules/", include("schedules.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/delivery/", include("delivery.urls")),
    path("api/dependents/", include("dependents.urls")),
    path("api/prescriptions/", include("prescriptions.urls")),
    path("api/medical_leaves/", include("medical_leaves.urls")),
]
