from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ordemServico.views import OrdemServicoViewSet, MiniOsViewSet
from ordemServico.views.TarefaMiniOSAPIView import TarefaMiniOSAPIView

# Cria o router da DRF
router = DefaultRouter()
router.register(r'api/ordens-servico', OrdemServicoViewSet, basename='apiordemservico')
router.register(r'api/minios', MiniOsViewSet, basename='apiminios')

# Inclui as URLs geradas pelo router no urlpatterns
urlpatterns = [
    path('', include(router.urls)),  # Registra todas as rotas criadas pelo router
    path("api/tarefas-minios/", TarefaMiniOSAPIView.as_view(), name="tarefas-minios"),
]
