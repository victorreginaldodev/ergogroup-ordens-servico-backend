from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.tarefas.models import Tarefa

Usuario = get_user_model()


class TarefaListSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    cliente_nome = serializers.CharField(source='servico.ordem_servico.cliente.nome', read_only=True)
    repositorio_nome = serializers.CharField(source='servico.repositorio.nome', read_only=True, default=None)

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'cliente_nome', 'repositorio_nome',
            'descricao', 'status', 'status_display', 'data_inicio', 'data_termino', 'atualizado_em',
        ]


class TarefaSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    responsavel = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Tarefa
        fields = [
            'id', 'servico', 'responsavel', 'responsavel_nome',
            'descricao', 'status', 'status_display',
            'data_inicio', 'data_termino', 'atualizado_em',
        ]
        read_only_fields = ['atualizado_em']
