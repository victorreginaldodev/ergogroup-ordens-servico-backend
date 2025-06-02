from django.urls import path
from ordemServico.views.area_tecnica.TarefasView import tecnico, atualizar_tarefa

urlpatterns = [
    path('tarefas/', tecnico, name='tarefas'),
    path('atualizar-tarefa/<int:tarefa_id>/', atualizar_tarefa, name='atualizar_tarefa'),
]