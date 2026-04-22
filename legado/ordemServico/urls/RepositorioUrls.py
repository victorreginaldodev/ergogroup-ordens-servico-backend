from django.urls import path
from legado.ordemServico.views.RepositorioView import repositorio

urlpatterns = [
    path('repositorio/', repositorio, name='repositorio'),
]