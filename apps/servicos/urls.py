from rest_framework.routers import DefaultRouter
from apps.servicos.views import RepositorioViewSet, ServicoViewSet

router = DefaultRouter()
router.register(r'repositorios', RepositorioViewSet, basename='servicos-repositorios')
router.register(r'servicos', ServicoViewSet, basename='servicos')

urlpatterns = router.urls
