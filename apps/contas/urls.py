from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.contas.views import UsuarioViewSet
from apps.contas.authentication.views import LoginView, RefreshView, LogoutView, MeView

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='contas-login'),
    path('auth/refresh/', RefreshView.as_view(), name='contas-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='contas-logout'),
    path('auth/me/', MeView.as_view(), name='contas-me'),
] + router.urls
