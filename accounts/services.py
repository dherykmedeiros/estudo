from django.db import transaction

from .models import UserPreference


def create_user_preferences(*, user) -> UserPreference:
    with transaction.atomic():
        preferences, _ = UserPreference.objects.get_or_create(user=user)
    return preferences


def update_user_preferences(*, preferences: UserPreference, currency: str, date_format: str) -> UserPreference:
    with transaction.atomic():
        preferences.currency = currency
        preferences.date_format = date_format
        preferences.full_clean()
        preferences.save()
    return preferences
