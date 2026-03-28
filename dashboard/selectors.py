from __future__ import annotations

from datetime import date

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from finances.models import Transaction, TransactionType
from finances.selectors import get_all_transactions, get_user_goals
from finances.services import calculate_balance


MONTHS_PT = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}


def obter_dados_evolucao_6_meses(user):
    today = date.today()
    month_limit = (today.month - 5) if today.month > 5 else 1
    base_qs = Transaction.objects.filter(user=user, data__year=today.year, data__month__gte=month_limit)

    grouped = (
        base_qs.annotate(mes=TruncMonth("data"))
        .values("mes", "tipo")
        .annotate(total=Sum("valor"))
        .order_by("mes")
    )

    labels = []
    entradas_map = {}
    saidas_map = {}

    for row in grouped:
        label = MONTHS_PT[row["mes"].month]
        if label not in labels:
            labels.append(label)
        if row["tipo"] == TransactionType.ENTRADA:
            entradas_map[label] = float(row["total"] or 0)
        else:
            saidas_map[label] = float(row["total"] or 0)

    entradas = [entradas_map.get(label, 0.0) for label in labels]
    saidas = [saidas_map.get(label, 0.0) for label in labels]

    return {
        "labels": labels,
        "series": [
            {"name": "Entradas", "data": entradas},
            {"name": "Saidas", "data": saidas},
        ],
    }


def obter_distribuicao_saidas_mes(user):
    today = date.today()
    rows = (
        Transaction.objects.filter(
            user=user,
            tipo=TransactionType.SAIDA,
            data__year=today.year,
            data__month=today.month,
        )
        .values("category__nome")
        .annotate(total=Sum("valor"))
        .order_by("-total")
    )

    labels = [row["category__nome"] or "Sem categoria" for row in rows]
    series = [float(row["total"] or 0) for row in rows]
    return {"labels": labels, "series": series}


def obter_dados_metas(user):
    goals = get_user_goals(user=user)
    if not goals.exists():
        return {
            "labels": ["Reserva", "Viagem", "Estudos"],
            "series": [38, 22, 40],
        }
    labels = [goal.nome for goal in goals]
    series = [round(goal.percentual_conclusao, 2) for goal in goals]
    return {"labels": labels, "series": series}


def obter_dados_investimentos(user):
    # Dados mockados ate a modelagem completa de investimentos.
    return {
        "labels": ["Renda Fixa", "Acoes", "FIIs", "Cripto"],
        "series": [45, 30, 15, 10],
    }


def obter_resumo_dashboard(user):
    transactions = get_all_transactions(user=user)
    return calculate_balance(transactions)
