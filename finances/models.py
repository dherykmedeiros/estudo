from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class TransactionType(models.TextChoices):
    ENTRADA = "entrada", "Entrada"
    SAIDA = "saida", "Saida"


class AccountType(models.TextChoices):
    CONTA_CORRENTE = "conta_corrente", "Conta Corrente"
    CARTEIRA = "carteira", "Carteira"
    CARTAO_CREDITO = "cartao_credito", "Cartao de Credito"


class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories")
    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=10, choices=TransactionType.choices)
    keywords = models.TextField(blank=True, default="")

    class Meta:
        unique_together = ("user", "nome", "tipo")
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.get_tipo_display()})"


class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    nome = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=AccountType.choices)

    class Meta:
        unique_together = ("user", "nome", "tipo")
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.nome} - {self.get_tipo_display()}"


class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="goals")
    nome = models.CharField(max_length=120)
    valor_alvo = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    valor_atual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), validators=[MinValueValidator(Decimal("0.00"))])

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome

    @property
    def percentual_conclusao(self) -> float:
        if self.valor_alvo <= 0:
            return 0.0
        pct = float((self.valor_atual / self.valor_alvo) * 100)
        return max(0.0, min(100.0, pct))


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=TransactionType.choices)
    descricao = models.CharField(max_length=255)

    class Meta:
        ordering = ["-data", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(valor__gt=0), name="transaction_valor_gt_zero"),
        ]

    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.descricao} - {self.valor}"
