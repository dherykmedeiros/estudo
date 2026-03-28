from .models import UserPreference


def get_user_preferences(*, user):
    return UserPreference.objects.get(user=user)
