from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.tarefas.models import MiniOS, RepositorioMiniOS
from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteListSerializer
from apps.tarefas.serializers.repositorio_mini_os_serializer import RepositorioMiniOSSerializer

Usuario = get_user_model()


class MiniOSListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MiniOS
        fields = [
            'id', 'cliente', 'cliente_nome', 'servico', 'servico_nome',
            'responsavel', 'responsavel_nome', 'status', 'status_display',
            'faturada', 'data_recebimento',
        ]


class MiniOSSerializer(serializers.ModelSerializer):
    cliente_detail = ClienteListSerializer(source='cliente', read_only=True)
    servico_detail = RepositorioMiniOSSerializer(source='servico', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    servico = serializers.PrimaryKeyRelatedField(queryset=RepositorioMiniOS.objects.all())
    responsavel = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = MiniOS
        fields = [
            'id', 'cliente', 'cliente_detail', 'servico', 'servico_detail',
            'responsavel', 'responsavel_nome', 'quantidade', 'descricao',
            'data_recebimento', 'data_inicio', 'data_termino',
            'status', 'status_display', 'revisao_cliente', 'faturada', 'numero_nf',
        ]
