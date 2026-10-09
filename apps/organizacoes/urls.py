from rest_framework.routers import DefaultRouter
from apps.organizacoes.views import OrganizacaoViewSet, SetorViewSet

router = DefaultRouter()
router.register(r'organizacoes', OrganizacaoViewSet, basename='organizacoes')
router.register(r'setores', SetorViewSet, basename='setores')

urlpatterns = router.urls
