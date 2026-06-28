from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.servicos.models import Servico, Repositorio
from apps.servicos.serializers.repositorio_serializer import RepositorioSerializer


class ServicoListSerializer(serializers.ModelSerializer):
    repositorio_nome = serializers.CharField(source='repositorio.nome', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cliente_nome = serializers.CharField(source='ordem_servico.cliente.nome', read_only=True, default='')
    data_criacao = serializers.DateField(source='ordem_servico.data_criacao', read_only=True, default=None)
    terminado_por_nome = serializers.SerializerMethodField()
    tem_tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'repositorio', 'repositorio_nome',
            'descricao', 'status', 'status_display', 'data_inicio',
            'data_termino', 'data_conclusao', 'terminado_por',
            'terminado_por_nome', 'criado_em', 'atualizado_em',
            'cliente_nome', 'data_criacao', 'tem_tarefas',
        ]

    @extend_schema_field(serializers.BooleanField())
    def get_tem_tarefas(self, obj):
        return obj.tarefas.exists()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_terminado_por_nome(self, obj):
        if not obj.terminado_por:
            return None
        usuario = obj.terminado_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username


class ServicoSerializer(serializers.ModelSerializer):
    repositorio_detail = RepositorioSerializer(source='repositorio', read_only=True)
    repositorio = serializers.PrimaryKeyRelatedField(
        queryset=Repositorio.objects.all(), allow_null=True, required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    terminado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'repositorio', 'repositorio_detail',
            'descricao', 'status', 'status_display', 'data_inicio',
            'data_termino', 'data_conclusao', 'terminado_por',
            'terminado_por_nome', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = [
            'status', 'data_inicio', 'data_termino', 'data_conclusao',
            'terminado_por', 'criado_em', 'atualizado_em',
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_terminado_por_nome(self, obj):
        if not obj.terminado_por:
            return None
        usuario = obj.terminado_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username
