from django.urls import path
from ordemServico.views.OrdemServicoView import listar_ordens_servicos, criar_ordem_servico, editar_ordem_servico

urlpatterns = [
    path('listar/ordens-servicos/', listar_ordens_servicos, name='listar_ordens_servicos'),
    path('criar/', criar_ordem_servico, name='criar_ordem_servico'),
    path('ordens-servicos/editar/<int:pk>/', editar_ordem_servico, name='editar_ordem_servico'),
]
