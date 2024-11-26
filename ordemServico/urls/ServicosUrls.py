from django.urls import path
from ordemServico.views.area_tecnica.ServicosView import *

urlpatterns = [
    path('lider/', lider_tecnico, name='lider_tecnico'),
    # path('tarefas/<int:servico_id>/', tarefas, name='tarefas'),
]
