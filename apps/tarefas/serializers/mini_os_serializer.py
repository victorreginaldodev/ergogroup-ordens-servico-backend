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
    liberada_cobranca_por_nome = serializers.SerializerMethodField()
    faturada_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = MiniOS
        fields = [
            'id', 'cliente', 'cliente_nome', 'servico', 'servico_nome',
            'responsavel', 'responsavel_nome', 'status', 'status_display',
            'revisao_cliente', 'gera_cobranca', 'data_liberacao_cobranca',
            'liberada_cobranca_por', 'liberada_cobranca_por_nome',
            'faturada', 'numero_nf', 'faturada_por', 'faturada_por_nome',
            'data_recebimento', 'data_inicio', 'data_termino',
            'criada_em', 'atualizado_em',
        ]

    def get_liberada_cobranca_por_nome(self, obj):
        if not obj.liberada_cobranca_por:
            return None
        usuario = obj.liberada_cobranca_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def get_faturada_por_nome(self, obj):
        if not obj.faturada_por:
            return None
        usuario = obj.faturada_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username


class MiniOSSerializer(serializers.ModelSerializer):
    cliente_detail = ClienteListSerializer(source='cliente', read_only=True)
    servico_detail = RepositorioMiniOSSerializer(source='servico', read_only=True)
    responsavel_nome = serializers.CharField(source='responsavel.nome_completo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    liberada_cobranca_por_nome = serializers.SerializerMethodField()
    faturada_por_nome = serializers.SerializerMethodField()

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    servico = serializers.PrimaryKeyRelatedField(queryset=RepositorioMiniOS.objects.all())
    responsavel = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = MiniOS
        fields = [
            'id', 'cliente', 'cliente_detail', 'servico', 'servico_detail',
            'responsavel', 'responsavel_nome', 'quantidade', 'descricao',
            'data_recebimento', 'data_inicio', 'data_termino',
            'status', 'status_display', 'revisao_cliente', 'gera_cobranca',
            'data_liberacao_cobranca', 'liberada_cobranca_por',
            'liberada_cobranca_por_nome', 'faturada', 'numero_nf',
            'faturada_por', 'faturada_por_nome',
            'criada_em', 'atualizado_em',
        ]
        read_only_fields = [
            'data_inicio', 'data_termino', 'criada_em', 'atualizado_em',
            'gera_cobranca', 'data_liberacao_cobranca',
            'liberada_cobranca_por', 'faturada_por',
        ]

    def get_liberada_cobranca_por_nome(self, obj):
        if not obj.liberada_cobranca_por:
            return None
        usuario = obj.liberada_cobranca_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def get_faturada_por_nome(self, obj):
        if not obj.faturada_por:
            return None
        usuario = obj.faturada_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if validated_data.get('faturada') is True and not instance.faturada:
                validated_data['faturada_por'] = request.user
        return super().update(instance, validated_data)
