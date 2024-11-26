from django.urls import path
from ordemServico.views.painel_controle.PainelControleView import *

urlpatterns = [
    path('painel/', painel_controle_template, name='painel_de_controle'),
    path('painel/dados/', painel_controle_dados, name='painel_controle_dados'),
    path('servico/<int:servico_id>/', detalhe_servico_modal, name='servico'),
    path('api/servicos-graficos/', servicos_graficos, name='servicos_graficos'),
]