from django.urls import path
from ordemServico.views.area_tecnica.ServicosView import *

urlpatterns = [
    path('servicos/', lista_servicos, name='lista_servicos'),
    path('atualizar-status-servico/<int:servico_id>/', atualizar_status_servico, name='atualizar_status_servico'),
    path('adicionar-tarefa/<int:servico_id>/', adicionar_tarefa, name='adicionar_tarefa'),
]
