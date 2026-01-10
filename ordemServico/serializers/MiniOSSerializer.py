from rest_framework import serializers
from ordemServico.models import MiniOS, Cliente, RepositorioMiniOS, Profile

class ClienteMiniOSSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'tipo_cliente', 'cliente_ativo']

class RepositorioMiniOSDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositorioMiniOS
        fields = ['id', 'nome', 'descricao']

class ProfileMiniOSSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'username', 'role']

class MiniOSSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniOS
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.cliente:
            representation['cliente'] = ClienteMiniOSSerializer(instance.cliente).data
        if instance.servico:
            representation['servico'] = RepositorioMiniOSDetailSerializer(instance.servico).data
        if instance.profile:
            representation['profile'] = ProfileMiniOSSerializer(instance.profile).data
        return representation


class MiniOSFaturamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MiniOS
        fields = ['id', 'faturamento', 'n_nf']
