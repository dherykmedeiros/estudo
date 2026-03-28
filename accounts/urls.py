from django.urls import path

from .views import FinTrackLoginView, FinTrackLogoutView, ProfilePreferenceView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", FinTrackLoginView.as_view(), name="login"),
    path("logout/", FinTrackLogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfilePreferenceView.as_view(), name="profile"),
]
