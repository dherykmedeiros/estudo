import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_non_staff_gets_403_on_admin_panel(client):
    user = get_user_model().objects.create_user(username="user", password="123456Strong")
    client.force_login(user)

    response = client.get(reverse("admin_panel:dashboard"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_gets_200_on_admin_panel(client):
    user = get_user_model().objects.create_user(username="staff", password="123456Strong", is_staff=True)
    client.force_login(user)

    response = client.get(reverse("admin_panel:dashboard"))
    assert response.status_code == 200
