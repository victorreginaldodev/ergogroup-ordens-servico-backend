from django.urls import path
from legado.ordemServico.views.UsuarioView import usuario

urlpatterns = [
    path('usuario/', usuario, name='usuario'),
]