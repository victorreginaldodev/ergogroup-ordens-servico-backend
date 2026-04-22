from rest_framework import serializers
from apps.servicos.models import Servico, Repositorio
from apps.servicos.serializers.repositorio_serializer import RepositorioSerializer


class ServicoListSerializer(serializers.ModelSerializer):
    repositorio_nome = serializers.CharField(source='repositorio.nome', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Servico
        fields = ['id', 'ordem_servico', 'repositorio', 'repositorio_nome', 'status', 'status_display', 'data_conclusao']


class ServicoSerializer(serializers.ModelSerializer):
    repositorio_detail = RepositorioSerializer(source='repositorio', read_only=True)
    repositorio = serializers.PrimaryKeyRelatedField(
        queryset=Repositorio.objects.all(), allow_null=True, required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'repositorio', 'repositorio_detail',
            'descricao', 'status', 'status_display', 'data_conclusao',
        ]
        read_only_fields = ['status', 'data_conclusao']
