from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

from apps.ordens_servico.models import Tarefa, Prioridade
from apps.catalogo.models import Complexidade

Usuario = get_user_model()


class TarefaListSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    cliente_nome = serializers.CharField(source='servico.ordem_servico.cliente.nome', read_only=True)
    catalogo_nome = serializers.CharField(source='servico.catalogo.nome', read_only=True, default=None)
    complexidade_servico = serializers.SerializerMethodField()
    horas_estimadas_efetivas = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'cliente_nome', 'catalogo_nome', 'complexidade_servico',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo',
            'horas_estimadas', 'horas_estimadas_efetivas',
            'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
        ]

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_complexidade_servico(self, obj):
        return obj.servico.complexidade_efetiva


class TarefaSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade = serializers.ChoiceField(choices=Prioridade.choices, required=False)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    complexidade_servico = serializers.SerializerMethodField()
    horas_estimadas_efetivas = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True, allow_null=True)
    responsavel = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo', 'complexidade_servico',
            'horas_estimadas', 'horas_estimadas_efetivas',
            'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
        ]
        read_only_fields = ['data_inicio', 'data_termino', 'criada_em', 'atualizado_em']

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_complexidade_servico(self, obj):
        return obj.servico.complexidade_efetiva

    def create(self, validated_data):
        if 'prioridade' not in validated_data:
            servico = validated_data.get('servico')
            if servico is not None:
                validated_data['prioridade'] = servico.prioridade
        return super().create(validated_data)
