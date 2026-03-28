from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from finances.models import AccountType
from finances.selectors import get_accounts_with_balances, get_user_goals

from .selectors import (
    obter_dados_evolucao_6_meses,
    obter_dados_investimentos,
    obter_dados_metas,
    obter_distribuicao_saidas_mes,
    obter_resumo_dashboard,
)


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["resumo"] = obter_resumo_dashboard(self.request.user)
        context["contas_correntes"] = get_accounts_with_balances(
            user=self.request.user,
            tipo=AccountType.CONTA_CORRENTE,
        )
        context["cartoes"] = get_accounts_with_balances(
            user=self.request.user,
            tipo=AccountType.CARTAO_CREDITO,
        )
        context["metas"] = get_user_goals(user=self.request.user)
        return context


class GraficoEvolucaoView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/grafico_evolucao.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart_data"] = obter_dados_evolucao_6_meses(self.request.user)
        context["chart_id"] = "chart-evolucao"
        return context


class GraficoSaidasView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/grafico_saidas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart_data"] = obter_distribuicao_saidas_mes(self.request.user)
        context["chart_id"] = "chart-saidas"
        return context


class GraficoMetasView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/grafico_metas.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart_data"] = obter_dados_metas(self.request.user)
        context["chart_id"] = "chart-metas"
        return context


class GraficoInvestimentosView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/grafico_investimentos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart_data"] = obter_dados_investimentos(self.request.user)
        context["chart_id"] = "chart-investimentos"
        return context
