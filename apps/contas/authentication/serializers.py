from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


def _usuario_payload(usuario):
    return {
        'id': usuario.id,
        'email': usuario.email,
        'username': usuario.username,
        'nome_completo': usuario.nome_completo,
        'tipo_usuario': usuario.tipo_usuario,
        'tipo_usuario_display': usuario.get_tipo_usuario_display(),
        'ativo': usuario.ativo,
        'is_staff': usuario.is_staff,
        'is_superuser': usuario.is_superuser,
    }


class LoginSerializer(TokenObtainPairSerializer):
    """Retorna access, refresh e dados do usuário autenticado."""

    # Garante o campo correto mesmo que o import do simplejwt aconteça antes
    # do registry do Django estar totalmente carregado (USERNAME_FIELD = 'email').
    username_field = 'email'

    def validate(self, attrs):
        print(">>> LOGIN attrs recebidos:", attrs)
        try:
            data = super().validate(attrs)
        except Exception as e:
            print(">>> LOGIN erro no super().validate:", type(e).__name__, e)
            raise
        print(">>> LOGIN usuário autenticado:", self.user)

        if not self.user.ativo:
            raise serializers.ValidationError('Usuário inativo. Entre em contato com o administrador.')

        data['usuario'] = _usuario_payload(self.user)
        return data


class TokenRefreshComUsuarioSerializer(TokenRefreshSerializer):
    """Refresh que devolve também os dados atualizados do usuário."""

    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            refresh = RefreshToken(attrs['refresh'])
            user_id = refresh['user_id']
            from django.contrib.auth import get_user_model
            Usuario = get_user_model()
            usuario = Usuario.objects.get(pk=user_id)
            data['usuario'] = _usuario_payload(usuario)
        except Exception:
            pass

        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            self._token = RefreshToken(value)
        except TokenError as e:
            raise serializers.ValidationError(str(e))
        return value

    def save(self):
        self._token.blacklist()
