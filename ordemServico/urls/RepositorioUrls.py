from django.urls import path
from ordemServico.views.RepositorioView import repositorio

urlpatterns = [
    path('repositorio/', repositorio, name='repositorio'),
]