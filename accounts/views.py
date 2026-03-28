from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from .forms import RegisterForm, UserPreferenceForm
from .selectors import get_user_preferences
from .services import create_user_preferences, update_user_preferences


class FinTrackLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class FinTrackLogoutView(LogoutView):
    next_page = reverse_lazy("landing_page")


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        create_user_preferences(user=self.object)
        return response


class ProfilePreferenceView(LoginRequiredMixin, FormView):
    template_name = "accounts/profile.html"
    form_class = UserPreferenceForm
    success_url = reverse_lazy("accounts:profile")

    @property
    def preference_obj(self):
        try:
            return get_user_preferences(user=self.request.user)
        except Exception:
            return create_user_preferences(user=self.request.user)

    def get_initial(self):
        preferences = self.preference_obj
        return {
            "currency": preferences.currency,
            "date_format": preferences.date_format,
        }

    def form_valid(self, form):
        update_user_preferences(preferences=self.preference_obj, **form.cleaned_data)
        messages.success(self.request, "Preferencias atualizadas com sucesso.")
        return super().form_valid(form)
