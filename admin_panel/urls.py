from django.urls import path

from .views import AdminDashboardView, AdminTransactionListView

app_name = "admin_panel"

urlpatterns = [
    path("", AdminDashboardView.as_view(), name="dashboard"),
    path("transactions/", AdminTransactionListView.as_view(), name="transactions"),
]
