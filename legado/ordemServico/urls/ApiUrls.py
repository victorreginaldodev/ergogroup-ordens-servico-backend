from django.urls import path, include
from rest_framework.routers import DefaultRouter
from legado.ordemServico.api import OrdemServicoViewSet, ProfileViewSet, ClienteViewSet, RepositorioViewSet, ServicoViewSet, TarefaViewSet, RepositorioMiniOSViewSet, MiniOSViewSet
from legado.ordemServico.api.FinanceiroKPIsAPIView import FinanceiroKPIsAPIView
from legado.ordemServico.api.AnaliseDadosAPIView import AnaliseDadosAPIView
from legado.ordemServico.views import MiniOsViewSet
from legado.ordemServico.views.TarefaMiniOSAPIView import TarefaMiniOSAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from legado.ordemServico.api.authentication import CustomTokenObtainPairView

# Cria o router da DRF
router = DefaultRouter()
router.register(r'api/ordens-servico', OrdemServicoViewSet, basename='apiordemservico')
router.register(r'api/profiles', ProfileViewSet, basename='apiprofiles')
router.register(r'api/clientes', ClienteViewSet, basename='apiclientes')
router.register(r'api/repositorios', RepositorioViewSet, basename='apirepositorios')
router.register(r'api/repositorios-minios', RepositorioMiniOSViewSet, basename='apirepositoriosminios')
router.register(r'api/servicos', ServicoViewSet, basename='apiservicos')
router.register(r'api/tarefas', TarefaViewSet, basename='apitarefas')
router.register(r'api/minios', MiniOSViewSet, basename='apiminios')

urlpatterns = [
    path('', include(router.urls)),
    path('api/tarefas-minios/', TarefaMiniOSAPIView.as_view(), name='tarefas-minios'),
    path('api/financeiro/kpis/', FinanceiroKPIsAPIView.as_view(), name='financeiro-kpis'),
    path('api/analise-dados/', AnaliseDadosAPIView.as_view(), name='analise-dados'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/usuarios/login/', CustomTokenObtainPairView.as_view(), name='usuarios_login'),
]
