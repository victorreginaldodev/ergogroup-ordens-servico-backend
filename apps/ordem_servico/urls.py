from rest_framework.routers import DefaultRouter
from apps.ordem_servico.views import OrdemServicoViewSet

router = DefaultRouter()
router.register(r'ordens', OrdemServicoViewSet, basename='ordens-servico')

urlpatterns = router.urls
