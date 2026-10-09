from rest_framework.routers import DefaultRouter
from apps.organizacoes.views import SetorViewSet

router = DefaultRouter()
router.register(r'setores', SetorViewSet, basename='setores')

urlpatterns = router.urls
