from django.urls import path
from apps.analise.views import AnaliseDadosView, FinanceiroKPIsView, ProdutividadeView

urlpatterns = [
    path('dados/', AnaliseDadosView.as_view(), name='analise-dados'),
    path('financeiro/kpis/', FinanceiroKPIsView.as_view(), name='analise-financeiro-kpis'),
    path('produtividade/', ProdutividadeView.as_view(), name='analise-produtividade'),
]
