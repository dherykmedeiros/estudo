from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterable

import pdfplumber
from django.core.exceptions import ValidationError
from django.db import transaction
from ofxparse import OfxParser

from .models import Account, Category, Goal, Transaction, TransactionType


def create_category(*, user, nome, tipo, keywords="") -> Category:
    with transaction.atomic():
        category = Category(
            user=user,
            nome=nome,
            tipo=tipo,
            keywords=keywords,
        )
        category.full_clean()
        category.save()
    return category


def update_category(*, category: Category, user, nome, tipo, keywords="") -> Category:
    if category.user_id != user.id:
        raise ValidationError("Categoria invalida para este usuario.")

    with transaction.atomic():
        category.nome = nome
        category.tipo = tipo
        category.keywords = keywords
        category.full_clean()
        category.save()
    return category


def delete_category(*, category: Category, user) -> None:
    if category.user_id != user.id:
        raise ValidationError("Categoria invalida para este usuario.")
    with transaction.atomic():
        category.delete()


def create_transaction(*, user, valor, data, tipo, descricao, account, category=None) -> Transaction:
    if not account:
        raise ValidationError("Conta e obrigatoria para registrar movimentacao.")
    if account.user_id != user.id:
        raise ValidationError("Conta invalida para este usuario.")

    with transaction.atomic():
        tx = Transaction(
            user=user,
            valor=valor,
            data=data,
            tipo=tipo,
            descricao=descricao,
            account=account,
            category=category,
        )
        tx.full_clean()
        tx.save()
    return tx


def update_transaction(*, transaction_obj: Transaction, user, valor, data, tipo, descricao, account, category=None) -> Transaction:
    if transaction_obj.user_id != user.id:
        raise ValidationError("Transacao invalida para este usuario.")
    if not account or account.user_id != user.id:
        raise ValidationError("Conta invalida para este usuario.")

    with transaction.atomic():
        transaction_obj.valor = valor
        transaction_obj.data = data
        transaction_obj.tipo = tipo
        transaction_obj.descricao = descricao
        transaction_obj.account = account
        transaction_obj.category = category
        transaction_obj.full_clean()
        transaction_obj.save()
    return transaction_obj


def delete_transaction(*, transaction_obj: Transaction, user) -> None:
    if transaction_obj.user_id != user.id:
        raise ValidationError("Transacao invalida para este usuario.")
    with transaction.atomic():
        transaction_obj.delete()


def create_goal(*, user, nome, valor_alvo, valor_atual=Decimal("0.00")) -> Goal:
    with transaction.atomic():
        goal = Goal(
            user=user,
            nome=nome,
            valor_alvo=valor_alvo,
            valor_atual=valor_atual,
        )
        goal.full_clean()
        goal.save()
    return goal


def update_goal(*, goal: Goal, user, nome, valor_alvo, valor_atual) -> Goal:
    if goal.user_id != user.id:
        raise ValidationError("Meta invalida para este usuario.")

    with transaction.atomic():
        goal.nome = nome
        goal.valor_alvo = valor_alvo
        goal.valor_atual = valor_atual
        goal.full_clean()
        goal.save()
    return goal


def delete_goal(*, goal: Goal, user) -> None:
    if goal.user_id != user.id:
        raise ValidationError("Meta invalida para este usuario.")
    with transaction.atomic():
        goal.delete()


def calculate_balance(transactions: Iterable[Transaction]) -> dict[str, Decimal]:
    entradas = Decimal("0.00")
    saidas = Decimal("0.00")
    for item in transactions:
        if item.tipo == TransactionType.ENTRADA:
            entradas += item.valor
        else:
            saidas += item.valor
    return {
        "entradas": entradas,
        "saidas": saidas,
        "saldo": entradas - saidas,
    }


def _normalize_keywords(raw: str) -> list[str]:
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def _get_or_create_avulsa_category(*, user, tipo: str = TransactionType.SAIDA) -> Category:
    category, _ = Category.objects.get_or_create(
        user=user,
        nome="Avulsa",
        tipo=tipo,
        defaults={"keywords": ""},
    )
    return category


def _resolve_category_by_description(*, user, descricao: str, tipo: str) -> Category:
    descricao_norm = (descricao or "").lower()
    categories = Category.objects.filter(user=user, tipo=tipo)
    for category in categories:
        for keyword in _normalize_keywords(category.keywords):
            if keyword in descricao_norm:
                return category
    return _get_or_create_avulsa_category(user=user, tipo=tipo)


def _parse_csv(file_obj) -> list[dict]:
    content = file_obj.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(content))
    headers = [header.lower() for header in (reader.fieldnames or [])]
    accepted_aliases = {
        "descricao": {"descricao", "description"},
        "valor": {"valor", "amount"},
        "data": {"data", "date"},
    }

    for required_field, aliases in accepted_aliases.items():
        if not any(alias in headers for alias in aliases):
            raise ValidationError(
                f"CSV invalido: coluna obrigatoria ausente para '{required_field}'."
            )

    rows = []
    for row in reader:
        rows.append(
            {
                "descricao": row.get("descricao") or row.get("description") or "",
                "valor": row.get("valor") or row.get("amount") or "0",
                "data": row.get("data") or row.get("date") or "",
                "tipo": row.get("tipo") or row.get("type") or "saida",
            }
        )
    if not rows:
        raise ValidationError("CSV vazio: nenhum registro encontrado para importacao.")
    return rows


def _parse_ofx(file_obj) -> list[dict]:
    content = file_obj.read()
    if isinstance(content, str):
        content = content.encode("utf-8")
    ofx = OfxParser.parse(io.BytesIO(content))
    rows = []
    for tx in ofx.account.statement.transactions:
        valor = Decimal(str(abs(tx.amount)))
        tipo = TransactionType.ENTRADA if tx.amount > 0 else TransactionType.SAIDA
        rows.append(
            {
                "descricao": tx.memo or tx.payee or "Movimentacao OFX",
                "valor": valor,
                "data": tx.date.date(),
                "tipo": tipo,
            }
        )
    return rows


def _parse_pdf(file_obj) -> list[dict]:
    # Fallback simples: cada linha "YYYY-MM-DD;descricao;valor;tipo"
    rows = []
    with pdfplumber.open(file_obj) as pdf:
        text_parts = []
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        raw = "\n".join(text_parts)

    for line in raw.splitlines():
        parts = [part.strip() for part in line.split(";")]
        if len(parts) != 4:
            continue
        rows.append(
            {
                "data": parts[0],
                "descricao": parts[1],
                "valor": parts[2],
                "tipo": parts[3].lower(),
            }
        )
    if not rows:
        raise ValidationError(
            "PDF invalido: use linhas no formato YYYY-MM-DD;descricao;valor;tipo."
        )
    return rows


def _normalize_row(row: dict, index: int) -> dict:
    raw_data = row.get("data")
    try:
        if isinstance(raw_data, date):
            data_val = raw_data
        else:
            data_val = date.fromisoformat(str(raw_data))
    except Exception as exc:
        raise ValidationError(
            f"Linha {index}: data invalida. Use o formato YYYY-MM-DD."
        ) from exc

    valor = row.get("valor", "0")
    try:
        if not isinstance(valor, Decimal):
            valor = Decimal(str(valor).replace(",", "."))
    except Exception as exc:
        raise ValidationError(f"Linha {index}: valor invalido.") from exc

    if abs(valor) <= 0:
        raise ValidationError(f"Linha {index}: valor deve ser maior que zero.")

    tipo = (row.get("tipo") or "saida").lower()
    if tipo not in {TransactionType.ENTRADA, TransactionType.SAIDA}:
        raise ValidationError(
            f"Linha {index}: tipo invalido. Use 'entrada' ou 'saida'."
        )

    descricao = str(row.get("descricao") or "").strip()
    if not descricao:
        raise ValidationError(f"Linha {index}: descricao obrigatoria.")

    return {
        "data": data_val,
        "descricao": descricao,
        "valor": abs(valor),
        "tipo": tipo,
    }


def _extract_rows(file_or_rows) -> list[dict]:
    if isinstance(file_or_rows, list):
        return file_or_rows

    name = getattr(file_or_rows, "name", "").lower()
    suffix = Path(name).suffix

    if suffix == ".csv":
        return _parse_csv(file_or_rows)
    if suffix == ".ofx":
        return _parse_ofx(file_or_rows)
    if suffix == ".pdf":
        return _parse_pdf(file_or_rows)

    raise ValidationError("Formato de arquivo nao suportado. Use CSV, OFX ou PDF.")


def process_bank_statement_import(file, user, account: Account) -> list[Transaction]:
    if account.user_id != user.id:
        raise ValidationError("Conta invalida para importacao.")

    extracted_rows = _extract_rows(file)
    normalized_rows = [_normalize_row(row, index + 1) for index, row in enumerate(extracted_rows)]
    created: list[Transaction] = []

    with transaction.atomic():
        for row in normalized_rows:
            category = _resolve_category_by_description(
                user=user,
                descricao=row["descricao"],
                tipo=row["tipo"],
            )
            created.append(
                Transaction.objects.create(
                    user=user,
                    account=account,
                    category=category,
                    valor=row["valor"],
                    data=row["data"],
                    tipo=row["tipo"],
                    descricao=row["descricao"],
                )
            )

    return created


def update_goal_progress(*, goal: Goal, valor_adicional: Decimal) -> Goal:
    with transaction.atomic():
        goal.valor_atual = goal.valor_atual + valor_adicional
        if goal.valor_atual < 0:
            goal.valor_atual = Decimal("0.00")
        goal.full_clean()
        goal.save()
    return goal
