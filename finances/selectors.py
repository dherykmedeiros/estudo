from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import DecimalField, Q, Sum
from django.db.models.functions import Coalesce

from .models import Account, AccountType, Category, Goal, Transaction, TransactionType


def get_all_transactions(*, user, start_date=None, end_date=None, query=None, category_id=None):
    qs = (
        Transaction.objects.filter(user=user)
        .select_related("category", "account")
        .order_by("-data", "-id")
    )
    if start_date:
        qs = qs.filter(data__gte=start_date)
    if end_date:
        qs = qs.filter(data__lte=end_date)
    if query:
        qs = qs.filter(descricao__icontains=query)
    if category_id:
        qs = qs.filter(category_id=category_id)
    return qs


def get_transaction_by_id(*, user, transaction_id: int):
    return Transaction.objects.select_related("category", "account").get(user=user, id=transaction_id)


def get_user_categories(*, user, tipo=None):
    qs = Category.objects.filter(user=user)
    if tipo:
        qs = qs.filter(tipo=tipo)
    return qs.order_by("nome")


def get_category_by_id(*, user, category_id: int):
    return Category.objects.get(user=user, id=category_id)


def get_user_accounts(*, user, tipo=None):
    qs = Account.objects.filter(user=user)
    if tipo:
        qs = qs.filter(tipo=tipo)
    return qs.order_by("nome")


def get_user_goals(*, user):
    return Goal.objects.filter(user=user).order_by("nome")


def get_goal_by_id(*, user, goal_id: int):
    return Goal.objects.get(user=user, id=goal_id)


def get_account_balance(account_id: int) -> Decimal:
    account = Account.objects.get(id=account_id)
    aggregates = account.transactions.aggregate(
        entradas=Coalesce(
            Sum("valor", filter=Q(tipo=TransactionType.ENTRADA)),
            Decimal("0.00"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        saidas=Coalesce(
            Sum("valor", filter=Q(tipo=TransactionType.SAIDA)),
            Decimal("0.00"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
    )

    entradas = aggregates["entradas"]
    saidas = aggregates["saidas"]

    if account.tipo == AccountType.CARTAO_CREDITO:
        return saidas
    return entradas - saidas


def get_accounts_with_balances(*, user, tipo=None):
    accounts = list(get_user_accounts(user=user, tipo=tipo))
    if not accounts:
        return accounts

    account_ids = [account.id for account in accounts]
    totals = (
        Transaction.objects.filter(user=user, account_id__in=account_ids)
        .values("account_id")
        .annotate(
            entradas=Coalesce(
                Sum("valor", filter=Q(tipo=TransactionType.ENTRADA)),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            saidas=Coalesce(
                Sum("valor", filter=Q(tipo=TransactionType.SAIDA)),
                Decimal("0.00"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
    )
    totals_by_account = {item["account_id"]: item for item in totals}

    for account in accounts:
        aggregate = totals_by_account.get(account.id, {"entradas": Decimal("0.00"), "saidas": Decimal("0.00")})
        if account.tipo == AccountType.CARTAO_CREDITO:
            account.saldo_atual = aggregate["saidas"]
        else:
            account.saldo_atual = aggregate["entradas"] - aggregate["saidas"]
    return accounts


def get_balance_summary(*, user):
    today = date.today()
    totals = (
        Transaction.objects.filter(user=user)
        .values("tipo")
        .annotate(total=Sum("valor"))
    )
    entradas = Decimal("0.00")
    saidas = Decimal("0.00")
    for row in totals:
        if row["tipo"] == TransactionType.ENTRADA:
            entradas = row["total"] or Decimal("0.00")
        else:
            saidas = row["total"] or Decimal("0.00")
    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": entradas - saidas,
        "mes": today.month,
        "ano": today.year,
    }
