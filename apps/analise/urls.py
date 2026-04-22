from django.urls import path
from apps.analise.views import AnaliseDadosView, FinanceiroKPIsView

urlpatterns = [
    path('dados/', AnaliseDadosView.as_view(), name='analise-dados'),
    path('financeiro/kpis/', FinanceiroKPIsView.as_view(), name='analise-financeiro-kpis'),
]
