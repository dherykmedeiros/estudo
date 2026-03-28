import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from finances.models import Goal


@pytest.mark.django_db
def test_dashboard_and_htmx_routes_return_200(client):
    user = get_user_model().objects.create_user(username="ana", password="123456Strong")
    client.force_login(user)

    assert client.get(reverse("dashboard:home")).status_code == 200
    assert client.get(reverse("dashboard:grafico_evolucao"), HTTP_HX_REQUEST="true").status_code == 200
    assert client.get(reverse("dashboard:grafico_saidas"), HTTP_HX_REQUEST="true").status_code == 200
    assert client.get(reverse("dashboard:grafico_metas"), HTTP_HX_REQUEST="true").status_code == 200
    assert client.get(reverse("dashboard:grafico_investimentos"), HTTP_HX_REQUEST="true").status_code == 200


@pytest.mark.django_db
def test_dashboard_renders_goal_progress_bar(client):
    user = get_user_model().objects.create_user(username="ana2", password="123456Strong")
    Goal.objects.create(user=user, nome="Reserva", valor_alvo="1000.00", valor_atual="250.00")
    client.force_login(user)

    response = client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    assert b"Progresso das Metas" in response.content
    assert b"Reserva" in response.content
