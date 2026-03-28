from django.contrib import admin
from django.urls import include, path

from core.views import LandingPageView

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="landing_page"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("finances/", include("finances.urls", namespace="finances")),
    path("dashboard/", include("dashboard.urls", namespace="dashboard")),
    path("admin-panel/", include("admin_panel.urls", namespace="admin_panel")),
]
