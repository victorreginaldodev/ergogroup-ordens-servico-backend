from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema

from apps.contas.authentication.serializers import (
    LoginSerializer,
    TokenRefreshComUsuarioSerializer,
    LogoutSerializer,
)
from apps.contas.serializers import UsuarioDetailSerializer


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        summary='Login',
        description='Autentica com e-mail e senha. Retorna access token, refresh token e dados do usuário.',
        responses={200: LoginSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
    serializer_class = TokenRefreshComUsuarioSerializer

    @extend_schema(
        summary='Renovar token',
        description='Renova o access token usando o refresh token. Retorna também os dados atualizados do usuário.',
        responses={200: TokenRefreshComUsuarioSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Logout',
        description='Invalida o refresh token. O cliente deve descartar o access token.',
        request=LogoutSerializer,
        responses={204: None},
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Usuário autenticado',
        description='Retorna os dados do usuário autenticado pelo token.',
        responses={200: UsuarioDetailSerializer},
    )
    def get(self, request):
        serializer = UsuarioDetailSerializer(request.user)
        return Response(serializer.data)
