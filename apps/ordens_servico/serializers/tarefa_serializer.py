from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.ordens_servico.models import Tarefa, Prioridade

Usuario = get_user_model()


class TarefaListSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    cliente_nome = serializers.CharField(source='servico.ordem_servico.cliente.nome', read_only=True)
    catalogo_nome = serializers.CharField(source='servico.catalogo.nome', read_only=True, default=None)

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'cliente_nome', 'catalogo_nome',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo',
            'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
        ]


class TarefaSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade = serializers.ChoiceField(choices=Prioridade.choices, required=False)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    responsavel = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'descricao', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'prazo',
            'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
        ]
        read_only_fields = ['data_inicio', 'data_termino', 'criada_em', 'atualizado_em']

    def create(self, validated_data):
        if 'prioridade' not in validated_data:
            servico = validated_data.get('servico')
            if servico is not None:
                validated_data['prioridade'] = servico.prioridade
        return super().create(validated_data)
