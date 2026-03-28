import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from finances.models import Account, AccountType, Transaction, TransactionType

from .models import UserPreference


@pytest.mark.django_db
def test_authenticated_user_is_redirected_from_login_and_register(client):
    user = get_user_model().objects.create_user(username="alreadyin", password="StrongPass123@")
    client.force_login(user)

    login_response = client.get(reverse("accounts:login"))
    register_response = client.get(reverse("accounts:register"))

    assert login_response.status_code == 302
    assert login_response.url == reverse("dashboard:home")
    assert register_response.status_code == 302
    assert register_response.url == reverse("dashboard:home")


@pytest.mark.django_db
def test_register_creates_default_user_preferences(client):
    response = client.post(
        reverse("accounts:register"),
        {
            "username": "prefuser",
            "password1": "StrongPass123@",
            "password2": "StrongPass123@",
        },
    )

    assert response.status_code == 302
    user = get_user_model().objects.get(username="prefuser")
    prefs = UserPreference.objects.get(user=user)
    assert prefs.currency == UserPreference.CurrencyChoices.BRL
    assert prefs.date_format == UserPreference.DateFormatChoices.DDMMYYYY


@pytest.mark.django_db
def test_profile_preferences_update(client):
    user = get_user_model().objects.create_user(username="profileuser", password="StrongPass123@")
    UserPreference.objects.create(user=user)
    client.force_login(user)

    response = client.post(
        reverse("accounts:profile"),
        {
            "currency": UserPreference.CurrencyChoices.USD,
            "date_format": UserPreference.DateFormatChoices.YYYYMMDD,
        },
    )

    assert response.status_code == 302
    prefs = UserPreference.objects.get(user=user)
    assert prefs.currency == UserPreference.CurrencyChoices.USD
    assert prefs.date_format == UserPreference.DateFormatChoices.YYYYMMDD


@pytest.mark.django_db
def test_login_redirects_to_dashboard(client):
    password = "StrongPass123@"
    get_user_model().objects.create_user(username="loginuser", password=password)

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "loginuser",
            "password": password,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("dashboard:home")


@pytest.mark.django_db
def test_anonymous_user_is_redirected_from_protected_routes(client):
    dashboard_response = client.get(reverse("dashboard:home"))
    account_create_response = client.post(
        reverse("finances:account_checking_create"),
        {"nome": "Conta Bloqueada", "tipo": AccountType.CONTA_CORRENTE},
    )

    assert dashboard_response.status_code == 302
    assert reverse("accounts:login") in dashboard_response.url
    assert account_create_response.status_code == 302
    assert reverse("accounts:login") in account_create_response.url


@pytest.mark.django_db
def test_logged_user_can_access_profile_and_create_account(client):
    user = get_user_model().objects.create_user(username="featureuser", password="StrongPass123@")
    client.force_login(user)

    profile_response = client.get(reverse("accounts:profile"))
    create_account_response = client.post(
        reverse("finances:account_checking_create"),
        {"nome": "Conta Principal", "tipo": AccountType.CONTA_CORRENTE},
    )
    dashboard_response = client.get(reverse("dashboard:home"))

    assert profile_response.status_code == 200
    assert UserPreference.objects.filter(user=user).exists()
    assert create_account_response.status_code == 302
    assert Account.objects.filter(user=user, nome="Conta Principal", tipo=AccountType.CONTA_CORRENTE).exists()
    assert dashboard_response.status_code == 200
    assert b"Sair" in profile_response.content


@pytest.mark.django_db
def test_dashboard_uses_currency_preference(client):
    user = get_user_model().objects.create_user(username="currencyuser", password="StrongPass123@")
    prefs = UserPreference.objects.create(user=user, currency=UserPreference.CurrencyChoices.USD)
    account = Account.objects.create(user=user, nome="Conta", tipo=AccountType.CONTA_CORRENTE)
    Transaction.objects.create(
        user=user,
        account=account,
        valor="1234.50",
        data="2026-03-20",
        tipo=TransactionType.ENTRADA,
        descricao="Recebimento",
    )
    client.force_login(user)

    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    assert b"$ 1,234.50" in response.content
    assert prefs.currency == UserPreference.CurrencyChoices.USD


@pytest.mark.django_db
def test_transaction_list_uses_date_preference(client):
    user = get_user_model().objects.create_user(username="dateuser", password="StrongPass123@")
    UserPreference.objects.create(user=user, date_format=UserPreference.DateFormatChoices.DDMMYYYY)
    account = Account.objects.create(user=user, nome="Conta", tipo=AccountType.CONTA_CORRENTE)
    Transaction.objects.create(
        user=user,
        account=account,
        valor="100.00",
        data="2026-03-21",
        tipo=TransactionType.SAIDA,
        descricao="Compra",
    )
    client.force_login(user)

    response = client.get(reverse("finances:transaction_list"))

    assert response.status_code == 200
    assert b"21/03/2026" in response.content
