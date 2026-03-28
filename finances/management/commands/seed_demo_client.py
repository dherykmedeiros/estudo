from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import UserPreference
from finances.models import Account, AccountType, Category, Goal, Transaction, TransactionType


class Command(BaseCommand):
    help = "Cria ou atualiza um cliente demo com dados financeiros para testes visuais e funcionais."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="cliente_demo", help="Username do cliente demo")
        parser.add_argument("--email", default="cliente_demo@example.com", help="Email do cliente demo")
        parser.add_argument("--password", default="Demo@123456", help="Senha do cliente demo")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        User = get_user_model()

        with transaction.atomic():
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": email},
            )
            user.email = email
            user.set_password(password)
            user.is_active = True
            user.save()

            UserPreference.objects.update_or_create(
                user=user,
                defaults={"currency": "BRL", "date_format": "dd/mm/yyyy"},
            )

            conta_corrente, _ = Account.objects.get_or_create(
                user=user,
                nome="Conta Principal",
                tipo=AccountType.CONTA_CORRENTE,
            )
            carteira, _ = Account.objects.get_or_create(
                user=user,
                nome="Carteira",
                tipo=AccountType.CARTEIRA,
            )
            cartao, _ = Account.objects.get_or_create(
                user=user,
                nome="Cartao Visa",
                tipo=AccountType.CARTAO_CREDITO,
            )

            categorias_data = [
                ("Salario", TransactionType.ENTRADA, "salario,pagamento,empresa"),
                ("Freelance", TransactionType.ENTRADA, "freela,freelance,projeto"),
                ("Alimentacao", TransactionType.SAIDA, "mercado,ifood,restaurante"),
                ("Transporte", TransactionType.SAIDA, "uber,99,combustivel"),
                ("Moradia", TransactionType.SAIDA, "aluguel,condominio,energia"),
                ("Lazer", TransactionType.SAIDA, "cinema,streaming,show"),
                ("Investimentos", TransactionType.ENTRADA, "investimento,rendimento"),
            ]
            categorias = {}
            for nome, tipo, keywords in categorias_data:
                category, _ = Category.objects.update_or_create(
                    user=user,
                    nome=nome,
                    tipo=tipo,
                    defaults={"keywords": keywords},
                )
                categorias[(nome, tipo)] = category

            Goal.objects.update_or_create(
                user=user,
                nome="Reserva de emergencia",
                defaults={"valor_alvo": Decimal("15000.00"), "valor_atual": Decimal("4200.00")},
            )
            Goal.objects.update_or_create(
                user=user,
                nome="Viagem internacional",
                defaults={"valor_alvo": Decimal("12000.00"), "valor_atual": Decimal("3100.00")},
            )
            Goal.objects.update_or_create(
                user=user,
                nome="Entrada apartamento",
                defaults={"valor_alvo": Decimal("60000.00"), "valor_atual": Decimal("9500.00")},
            )

            hoje = date.today()
            tx_data = [
                {
                    "fingerprint": "seed-001",
                    "account": conta_corrente,
                    "category": categorias[("Salario", TransactionType.ENTRADA)],
                    "valor": Decimal("8500.00"),
                    "data": hoje.replace(day=1),
                    "tipo": TransactionType.ENTRADA,
                    "descricao": "Salario mensal",
                },
                {
                    "fingerprint": "seed-002",
                    "account": conta_corrente,
                    "category": categorias[("Freelance", TransactionType.ENTRADA)],
                    "valor": Decimal("1800.00"),
                    "data": hoje - timedelta(days=3),
                    "tipo": TransactionType.ENTRADA,
                    "descricao": "Projeto website freelance",
                },
                {
                    "fingerprint": "seed-003",
                    "account": conta_corrente,
                    "category": categorias[("Moradia", TransactionType.SAIDA)],
                    "valor": Decimal("2100.00"),
                    "data": hoje.replace(day=5),
                    "tipo": TransactionType.SAIDA,
                    "descricao": "Aluguel",
                },
                {
                    "fingerprint": "seed-004",
                    "account": conta_corrente,
                    "category": categorias[("Alimentacao", TransactionType.SAIDA)],
                    "valor": Decimal("420.35"),
                    "data": hoje - timedelta(days=6),
                    "tipo": TransactionType.SAIDA,
                    "descricao": "Compras mercado",
                },
                {
                    "fingerprint": "seed-005",
                    "account": carteira,
                    "category": categorias[("Transporte", TransactionType.SAIDA)],
                    "valor": Decimal("76.40"),
                    "data": hoje - timedelta(days=4),
                    "tipo": TransactionType.SAIDA,
                    "descricao": "Corridas de app",
                },
                {
                    "fingerprint": "seed-006",
                    "account": cartao,
                    "category": categorias[("Lazer", TransactionType.SAIDA)],
                    "valor": Decimal("89.90"),
                    "data": hoje - timedelta(days=8),
                    "tipo": TransactionType.SAIDA,
                    "descricao": "Streaming e musica",
                },
                {
                    "fingerprint": "seed-007",
                    "account": cartao,
                    "category": categorias[("Alimentacao", TransactionType.SAIDA)],
                    "valor": Decimal("145.20"),
                    "data": hoje - timedelta(days=2),
                    "tipo": TransactionType.SAIDA,
                    "descricao": "Jantar restaurante",
                },
                {
                    "fingerprint": "seed-008",
                    "account": conta_corrente,
                    "category": categorias[("Investimentos", TransactionType.ENTRADA)],
                    "valor": Decimal("310.00"),
                    "data": hoje - timedelta(days=1),
                    "tipo": TransactionType.ENTRADA,
                    "descricao": "Rendimento CDB",
                },
            ]

            created_count = 0
            for item in tx_data:
                _, was_created = Transaction.objects.update_or_create(
                    user=user,
                    account=item["account"],
                    import_fingerprint=item["fingerprint"],
                    defaults={
                        "category": item["category"],
                        "valor": item["valor"],
                        "data": item["data"],
                        "tipo": item["tipo"],
                        "descricao": item["descricao"],
                    },
                )
                if was_created:
                    created_count += 1

        status = "criado" if created else "atualizado"
        self.stdout.write(self.style.SUCCESS("Cliente demo preparado com sucesso."))
        self.stdout.write(f"Usuario: {username} ({status})")
        self.stdout.write(f"Senha: {password}")
        self.stdout.write(f"Transacoes inseridas nesta execucao: {created_count}")
        self.stdout.write(
            f"Total de transacoes do cliente: {Transaction.objects.filter(user=user).count()}"
        )
