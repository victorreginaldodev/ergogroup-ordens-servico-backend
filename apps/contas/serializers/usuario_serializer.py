from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from apps.contas.models.choices import TipoUsuario

Usuario = get_user_model()


class UsuarioListSerializer(serializers.ModelSerializer):
    tipo_usuario_display = serializers.CharField(source='get_tipo_usuario_display', read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome_completo', 'tipo_usuario', 'tipo_usuario_display', 'ativo', 'data_criacao']


class UsuarioDetailSerializer(serializers.ModelSerializer):
    tipo_usuario_display = serializers.CharField(source='get_tipo_usuario_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'username', 'nome_completo',
            'tipo_usuario', 'tipo_usuario_display',
            'ativo', 'is_staff', 'is_superuser',
            'data_criacao', 'last_login',
        ]
        read_only_fields = ['data_criacao', 'last_login']


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirmacao = serializers.CharField(write_only=True)
    tipo_usuario_display = serializers.CharField(source='get_tipo_usuario_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'username', 'nome_completo',
            'tipo_usuario', 'tipo_usuario_display',
            'ativo', 'password', 'password_confirmacao',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirmacao'):
            raise serializers.ValidationError({'password_confirmacao': 'As senhas não coincidem.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    tipo_usuario_display = serializers.CharField(source='get_tipo_usuario_display', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'username', 'nome_completo',
            'tipo_usuario', 'tipo_usuario_display', 'ativo',
        ]
        read_only_fields = ['id']


class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True, validators=[validate_password])
    nova_senha_confirmacao = serializers.CharField(write_only=True)

    def validate_senha_atual(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value

    def validate(self, attrs):
        if attrs['nova_senha'] != attrs['nova_senha_confirmacao']:
            raise serializers.ValidationError({'nova_senha_confirmacao': 'As senhas não coincidem.'})
        return attrs
