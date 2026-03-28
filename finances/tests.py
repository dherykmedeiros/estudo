from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Account, AccountType, Category, Goal, Transaction, TransactionType
from .selectors import get_account_balance
from .services import create_goal, create_transaction, process_bank_statement_import, update_goal_progress


@pytest.mark.django_db
def test_models_str_and_positive_values():
    user = get_user_model().objects.create_user(username="lucas", password="123456Strong")
    account = Account.objects.create(user=user, nome="Nubank", tipo=AccountType.CONTA_CORRENTE)
    category = Category.objects.create(user=user, nome="Transporte", tipo=TransactionType.SAIDA, keywords="uber")
    tx = Transaction.objects.create(
        user=user,
        account=account,
        category=category,
        valor=Decimal("10.00"),
        data=date.today(),
        tipo=TransactionType.SAIDA,
        descricao="Uber trip",
    )

    assert "Nubank" in str(account)
    assert "Transporte" in str(category)
    assert "Uber" in str(tx)


@pytest.mark.django_db
def test_transaction_requires_account():
    user = get_user_model().objects.create_user(username="maria", password="123456Strong")
    with pytest.raises(ValidationError):
        create_transaction(
            user=user,
            valor=Decimal("50.00"),
            data=date.today(),
            tipo=TransactionType.ENTRADA,
            descricao="Freela",
            account=None,
            category=None,
        )


@pytest.mark.django_db
def test_get_account_balance_for_checking_and_credit_card():
    user = get_user_model().objects.create_user(username="joao", password="123456Strong")
    conta = Account.objects.create(user=user, nome="Inter", tipo=AccountType.CONTA_CORRENTE)
    cartao = Account.objects.create(user=user, nome="Visa", tipo=AccountType.CARTAO_CREDITO)

    Transaction.objects.create(user=user, account=conta, valor=Decimal("100.00"), data=date.today(), tipo=TransactionType.ENTRADA, descricao="Salario")
    Transaction.objects.create(user=user, account=conta, valor=Decimal("30.00"), data=date.today(), tipo=TransactionType.SAIDA, descricao="Mercado")
    Transaction.objects.create(user=user, account=cartao, valor=Decimal("70.00"), data=date.today(), tipo=TransactionType.SAIDA, descricao="Restaurante")

    assert get_account_balance(conta.id) == Decimal("70")
    assert get_account_balance(cartao.id) == Decimal("70")


@pytest.mark.django_db
def test_import_service_auto_categorization_and_avulsa_fallback():
    user = get_user_model().objects.create_user(username="bia", password="123456Strong")
    account = Account.objects.create(user=user, nome="Carteira", tipo=AccountType.CARTEIRA)
    Category.objects.create(user=user, nome="Transporte", tipo=TransactionType.SAIDA, keywords="uber,99")

    rows = [
        {"descricao": "UBER TRIP", "valor": "25.50", "data": "2026-03-10", "tipo": "saida"},
        {"descricao": "TARIFA BANCARIA", "valor": "9.90", "data": "2026-03-11", "tipo": "saida"},
    ]

    created = process_bank_statement_import(rows, user, account)
    assert len(created) == 2

    uber_tx = Transaction.objects.get(descricao="UBER TRIP")
    tarifa_tx = Transaction.objects.get(descricao="TARIFA BANCARIA")

    assert uber_tx.category.nome == "Transporte"
    assert tarifa_tx.category.nome == "Avulsa"


@pytest.mark.django_db
def test_account_crud_routes_separated_by_type(client):
    user = get_user_model().objects.create_user(username="roberta", password="123456Strong")
    client.force_login(user)

    create_cc = client.post(reverse("finances:account_checking_create"), {"nome": "Inter", "tipo": AccountType.CONTA_CORRENTE})
    create_card = client.post(reverse("finances:account_credit_card_create"), {"nome": "Master", "tipo": AccountType.CARTAO_CREDITO})

    assert create_cc.status_code == 302
    assert create_card.status_code == 302

    conta = Account.objects.get(user=user, nome="Inter")
    cartao = Account.objects.get(user=user, nome="Master")

    update_cc = client.post(reverse("finances:account_checking_update", args=[conta.id]), {"nome": "Inter PF", "tipo": AccountType.CONTA_CORRENTE})
    update_card = client.post(reverse("finances:account_credit_card_update", args=[cartao.id]), {"nome": "Master Black", "tipo": AccountType.CARTAO_CREDITO})

    assert update_cc.status_code == 302
    assert update_card.status_code == 302

    assert Account.objects.filter(user=user, nome="Inter PF", tipo=AccountType.CONTA_CORRENTE).exists()
    assert Account.objects.filter(user=user, nome="Master Black", tipo=AccountType.CARTAO_CREDITO).exists()


@pytest.mark.django_db
def test_goal_crud_routes(client):
    user = get_user_model().objects.create_user(username="metauser", password="123456Strong")
    client.force_login(user)

    create_response = client.post(
        reverse("finances:goal_create"),
        {"nome": "Reserva", "valor_alvo": "1000.00", "valor_atual": "100.00"},
    )
    assert create_response.status_code == 302

    goal = Goal.objects.get(user=user, nome="Reserva")

    update_response = client.post(
        reverse("finances:goal_update", args=[goal.id]),
        {"nome": "Reserva Emergencia", "valor_alvo": "1200.00", "valor_atual": "250.00"},
    )
    assert update_response.status_code == 302
    assert Goal.objects.filter(user=user, nome="Reserva Emergencia").exists()

    delete_response = client.post(reverse("finances:goal_delete", args=[goal.id]))
    assert delete_response.status_code == 302
    assert not Goal.objects.filter(user=user, id=goal.id).exists()


@pytest.mark.django_db
def test_goal_services_progress_update():
    user = get_user_model().objects.create_user(username="servicegoal", password="123456Strong")
    goal = create_goal(user=user, nome="Notebook", valor_alvo=Decimal("5000.00"), valor_atual=Decimal("0.00"))

    goal = update_goal_progress(goal=goal, valor_adicional=Decimal("350.00"))
    assert goal.valor_atual == Decimal("350.00")

    goal = update_goal_progress(goal=goal, valor_adicional=Decimal("-700.00"))
    assert goal.valor_atual == Decimal("0.00")


@pytest.mark.django_db
def test_category_crud_routes(client):
    user = get_user_model().objects.create_user(username="catuser", password="123456Strong")
    client.force_login(user)

    create_response = client.post(
        reverse("finances:category_create"),
        {"nome": "Alimentacao", "tipo": TransactionType.SAIDA, "keywords": "mercado,ifood"},
    )
    assert create_response.status_code == 302

    category = Category.objects.get(user=user, nome="Alimentacao")

    update_response = client.post(
        reverse("finances:category_update", args=[category.id]),
        {"nome": "Supermercado", "tipo": TransactionType.SAIDA, "keywords": "mercado,atacadao"},
    )
    assert update_response.status_code == 302
    assert Category.objects.filter(user=user, nome="Supermercado").exists()

    delete_response = client.post(reverse("finances:category_delete", args=[category.id]))
    assert delete_response.status_code == 302
    assert not Category.objects.filter(user=user, id=category.id).exists()


@pytest.mark.django_db
def test_transaction_list_filter_by_category(client):
    user = get_user_model().objects.create_user(username="filteruser", password="123456Strong")
    client.force_login(user)

    account = Account.objects.create(user=user, nome="Conta", tipo=AccountType.CONTA_CORRENTE)
    cat_transporte = Category.objects.create(user=user, nome="Transporte", tipo=TransactionType.SAIDA, keywords="uber")
    cat_lazer = Category.objects.create(user=user, nome="Lazer", tipo=TransactionType.SAIDA, keywords="cinema")

    Transaction.objects.create(
        user=user,
        account=account,
        category=cat_transporte,
        valor=Decimal("30.00"),
        data=date.today(),
        tipo=TransactionType.SAIDA,
        descricao="Uber",
    )
    Transaction.objects.create(
        user=user,
        account=account,
        category=cat_lazer,
        valor=Decimal("50.00"),
        data=date.today(),
        tipo=TransactionType.SAIDA,
        descricao="Cinema",
    )

    response = client.get(reverse("finances:transaction_list"), {"category": str(cat_transporte.id)})

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Uber" in content
    assert "Cinema" not in content


@pytest.mark.django_db
def test_transaction_list_pagination(client):
    user = get_user_model().objects.create_user(username="pageuser", password="123456Strong")
    client.force_login(user)

    account = Account.objects.create(user=user, nome="Conta", tipo=AccountType.CONTA_CORRENTE)
    category = Category.objects.create(user=user, nome="Diversos", tipo=TransactionType.SAIDA)

    for idx in range(10):
        Transaction.objects.create(
            user=user,
            account=account,
            category=category,
            valor=Decimal("10.00"),
            data=date.today(),
            tipo=TransactionType.SAIDA,
            descricao=f"Despesa {idx}",
        )

    response = client.get(reverse("finances:transaction_list"), {"page": 2})

    assert response.status_code == 200
    assert response.context["is_paginated"] is True
    assert response.context["page_obj"].number == 2


@pytest.mark.django_db
def test_import_service_invalid_row_returns_friendly_message():
    user = get_user_model().objects.create_user(username="importmsg", password="123456Strong")
    account = Account.objects.create(user=user, nome="Carteira", tipo=AccountType.CARTEIRA)

    rows = [
        {"descricao": "", "valor": "0", "data": "2026-03-10", "tipo": "saida"},
    ]

    with pytest.raises(ValidationError) as exc_info:
        process_bank_statement_import(rows, user, account)

    assert "Linha 1" in str(exc_info.value)


@pytest.mark.django_db
def test_transaction_import_view_creates_transactions_from_csv(client):
    user = get_user_model().objects.create_user(username="importview", password="123456Strong")
    account = Account.objects.create(user=user, nome="Conta Import", tipo=AccountType.CONTA_CORRENTE)
    client.force_login(user)

    csv_content = "descricao,valor,data,tipo\nUBER TRIP,25.50,2026-03-10,saida\nSALARIO,1000.00,2026-03-11,entrada\n"
    upload = SimpleUploadedFile("extrato.csv", csv_content.encode("utf-8"), content_type="text/csv")

    response = client.post(
        reverse("finances:transaction_import"),
        {"account": str(account.id), "statement_file": upload},
    )

    assert response.status_code == 302
    assert Transaction.objects.filter(user=user, account=account, descricao="UBER TRIP").exists()
    assert Transaction.objects.filter(user=user, account=account, descricao="SALARIO").exists()


@pytest.mark.django_db
def test_transaction_import_view_rejects_invalid_extension(client):
    user = get_user_model().objects.create_user(username="importinvalid", password="123456Strong")
    account = Account.objects.create(user=user, nome="Conta Import", tipo=AccountType.CONTA_CORRENTE)
    client.force_login(user)

    upload = SimpleUploadedFile("extrato.txt", b"invalido", content_type="text/plain")

    response = client.post(
        reverse("finances:transaction_import"),
        {"account": str(account.id), "statement_file": upload},
    )

    assert response.status_code == 200
    assert b"Formato invalido" in response.content


@pytest.mark.django_db
def test_transaction_import_requires_authentication(client):
    response = client.get(reverse("finances:transaction_import"))
    assert response.status_code == 302
    assert reverse("accounts:login") in response.url
