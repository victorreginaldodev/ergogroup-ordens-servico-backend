from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.ordens_servico.models import Servico, Prioridade
from apps.catalogo.models import Catalogo, Complexidade
from apps.catalogo.serializers import CatalogoSerializer


class ServicoListSerializer(serializers.ModelSerializer):
    catalogo_nome = serializers.CharField(source='catalogo.nome', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    complexidade_display = serializers.SerializerMethodField()
    horas_estimadas_efetivas = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)
    complexidade_efetiva = serializers.IntegerField(read_only=True, allow_null=True)
    cliente_nome = serializers.CharField(source='ordem_servico.cliente.nome', read_only=True, default='')
    data_venda = serializers.DateField(source='ordem_servico.data_venda', read_only=True, default=None)
    terminado_por_nome = serializers.SerializerMethodField()
    tem_tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'catalogo', 'catalogo_nome',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo',
            'horas_estimadas', 'horas_estimadas_efetivas',
            'complexidade', 'complexidade_display', 'complexidade_efetiva',
            'data_inicio', 'data_termino', 'data_conclusao', 'terminado_por',
            'terminado_por_nome', 'criado_em', 'atualizado_em',
            'cliente_nome', 'data_venda', 'tem_tarefas',
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_complexidade_display(self, obj):
        if obj.complexidade_efetiva is None:
            return None
        return Complexidade(obj.complexidade_efetiva).label

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
    catalogo_detail = CatalogoSerializer(source='catalogo', read_only=True)
    catalogo = serializers.PrimaryKeyRelatedField(
        queryset=Catalogo.objects.all(), allow_null=True, required=False
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade = serializers.ChoiceField(choices=Prioridade.choices, required=False)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    complexidade_display = serializers.SerializerMethodField()
    horas_estimadas_efetivas = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)
    complexidade_efetiva = serializers.IntegerField(read_only=True, allow_null=True)
    terminado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = [
            'id', 'ordem_servico', 'catalogo', 'catalogo_detail',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo',
            'horas_estimadas', 'horas_estimadas_efetivas',
            'complexidade', 'complexidade_display', 'complexidade_efetiva',
            'data_inicio', 'data_termino', 'data_conclusao', 'terminado_por',
            'terminado_por_nome', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = [
            'status', 'data_inicio', 'data_termino', 'data_conclusao',
            'terminado_por', 'criado_em', 'atualizado_em',
        ]

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_complexidade_display(self, obj):
        if obj.complexidade_efetiva is None:
            return None
        return Complexidade(obj.complexidade_efetiva).label

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_terminado_por_nome(self, obj):
        if not obj.terminado_por:
            return None
        usuario = obj.terminado_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def create(self, validated_data):
        if 'prioridade' not in validated_data:
            ordem_servico = validated_data.get('ordem_servico')
            if ordem_servico is not None:
                validated_data['prioridade'] = ordem_servico.prioridade

        catalogo = validated_data.get('catalogo')
        if catalogo is not None:
            if 'horas_estimadas' not in validated_data:
                validated_data['horas_estimadas'] = catalogo.horas_estimadas
            if 'complexidade' not in validated_data:
                validated_data['complexidade'] = catalogo.complexidade

        return super().create(validated_data)
