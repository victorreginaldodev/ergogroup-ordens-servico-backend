from rest_framework import serializers
from ordemServico.models import MiniOS, RepositorioMiniOS, Profile, Cliente


class ClienteMiniOsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = ['nome', 'tipo_cliente', 'cliente_ativo']


class ProfileMiniOsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ['user_name']


class RepositorioMiniOsSerializer(serializers.ModelSerializer):

    class Meta:
        model = RepositorioMiniOS
        exclude = ['descricao']


class MiniOsSerializer(serializers.ModelSerializer):
    cliente = ClienteMiniOsSerializer()
    profile = ProfileMiniOsSerializer()
    servico = RepositorioMiniOsSerializer()

    class Meta:
        model = MiniOS
        exclude = ['descricao']