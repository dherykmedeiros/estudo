from django.urls import path

from .views import (
    DashboardHomeView,
    GraficoEvolucaoView,
    GraficoInvestimentosView,
    GraficoMetasView,
    GraficoSaidasView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("grafico-evolucao/", GraficoEvolucaoView.as_view(), name="grafico_evolucao"),
    path("grafico-saidas/", GraficoSaidasView.as_view(), name="grafico_saidas"),
    path("grafico-metas/", GraficoMetasView.as_view(), name="grafico_metas"),
    path("grafico-investimentos/", GraficoInvestimentosView.as_view(), name="grafico_investimentos"),
]
