from django.urls import path
from ordemServico.views.painel_controle.PainelControleView import *

urlpatterns = [
    path('painel/', painel_controle_template, name='painel_de_controle'),
    path('api/servicos-graficos/', servicos_graficos, name='servicos_graficos'),
]