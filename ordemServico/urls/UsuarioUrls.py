from django.urls import path
from ordemServico.views.UsuarioView import usuario

urlpatterns = [
    path('usuario/', usuario, name='usuario'),
]