import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_landing_page_status_200(client):
    response = client.get(reverse("landing_page"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_status_200(client):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_status_200(client):
    response = client.get(reverse("accounts:register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_redirects_to_dashboard_when_user_is_authenticated(client):
    user = get_user_model().objects.create_user(username="landauth", password="123456Strong")
    client.force_login(user)

    response = client.get(reverse("landing_page"))
    assert response.status_code == 302
    assert response.url == reverse("dashboard:home")


@pytest.mark.django_db
def test_global_nav_is_available_on_protected_pages(client):
    user = get_user_model().objects.create_user(username="navauth", password="123456Strong")
    client.force_login(user)

    response = client.get(reverse("finances:transaction_list"))

    assert response.status_code == 200
    assert b"Dashboard" in response.content
    assert b"Sair" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "dashboard:home",
        "dashboard:grafico_evolucao",
        "dashboard:grafico_saidas",
        "dashboard:grafico_metas",
        "dashboard:grafico_investimentos",
        "finances:transaction_list",
        "finances:transaction_create",
        "finances:transaction_import",
        "finances:category_list",
        "finances:goal_list",
        "finances:account_checking_list",
        "finances:account_credit_card_list",
        "accounts:profile",
    ],
)
def test_protected_routes_require_login(client, url_name):
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url
