from django.urls import path
from ordemServico.views.ClientesView import criar_cliente, listar_clientes, editar_cliente

urlpatterns = [
    path('criar/cliente/', criar_cliente, name='criar_cliente'),
    path('listar/clientes/', listar_clientes, name='listar_clientes'),
    path('editar/cliente/<int:cliente_id>/', editar_cliente, name='editar_cliente'), 
]
