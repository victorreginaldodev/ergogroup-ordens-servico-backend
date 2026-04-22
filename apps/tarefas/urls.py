from rest_framework.routers import DefaultRouter
from apps.tarefas.views import RepositorioMiniOSViewSet, TarefaViewSet, MiniOSViewSet

router = DefaultRouter()
router.register(r'repositorios', RepositorioMiniOSViewSet, basename='tarefas-repositorios')
router.register(r'tarefas', TarefaViewSet, basename='tarefas')
router.register(r'mini-os', MiniOSViewSet, basename='mini-os')

urlpatterns = router.urls
