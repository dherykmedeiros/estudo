from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm

from .models import UserPreference


class RegisterForm(UserCreationForm):
    pass


class UserPreferenceForm(ModelForm):
    class Meta:
        model = UserPreference
        fields = ["currency", "date_format"]
        widgets = {
            "currency": forms.Select(
                attrs={
                    "class": "w-full rounded-xl bg-zinc-900/50 border border-zinc-700 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-violet-500 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
                }
            ),
            "date_format": forms.Select(
                attrs={
                    "class": "w-full rounded-xl bg-zinc-900/50 border border-zinc-700 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-violet-500 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
                }
            ),
        }
