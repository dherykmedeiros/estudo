from django.conf import settings
from django.db import models


class UserPreference(models.Model):
    class CurrencyChoices(models.TextChoices):
        BRL = "BRL", "Real (BRL)"
        USD = "USD", "Dollar (USD)"
        EUR = "EUR", "Euro (EUR)"

    class DateFormatChoices(models.TextChoices):
        DDMMYYYY = "dd/mm/yyyy", "DD/MM/YYYY"
        YYYYMMDD = "yyyy-mm-dd", "YYYY-MM-DD"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences")
    currency = models.CharField(max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.BRL)
    date_format = models.CharField(max_length=10, choices=DateFormatChoices.choices, default=DateFormatChoices.DDMMYYYY)

    def __str__(self) -> str:
        return f"Preferencias de {self.user.username}"
