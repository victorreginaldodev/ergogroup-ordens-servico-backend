from rest_framework import serializers
from apps.servicos.models import Servico, Repositorio
from apps.servicos.serializers.repositorio_serializer import RepositorioSerializer


class ServicoListSerializer(serializers.ModelSerializer):
    repositorio_nome = serializers.CharField(source='repositorio.nome', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cliente_nome = serializers.CharField(source='ordem_servico.cliente.nome', read_only=True, default='')
    data_criacao = serializers.DateField(source='ordem_servico.data_criacao', read_only=True, default=None)
    tem_tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'repositorio', 'repositorio_nome',
            'descricao', 'status', 'status_display', 'data_conclusao',
            'cliente_nome', 'data_criacao', 'tem_tarefas',
        ]

    def get_tem_tarefas(self, obj):
        return obj.tarefas.exists()


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
        read_only_fields = ['data_conclusao']
