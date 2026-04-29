from rest_framework import serializers
from apps.ordem_servico.models import OrdemServico
from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteListSerializer, ClienteSerializer


class OrdemServicoListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'cliente', 'cliente_nome', 'data_criacao', 'valor',
            'forma_pagamento', 'forma_pagamento_display',
            'concluida', 'faturada', 'cobranca_imediata',
        ]


class OrdemServicoSerializer(serializers.ModelSerializer):
    cliente_detail = ClienteSerializer(source='cliente', read_only=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    liberada_para_faturamento = serializers.SerializerMethodField()
    criado_por_nome = serializers.SerializerMethodField()
    data_conclusao_os = serializers.SerializerMethodField()
    finalizador_nome = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'cliente', 'cliente_detail',
            'criado_por', 'criado_por_nome', 'data_criacao', 'valor',
            'forma_pagamento', 'forma_pagamento_display', 'quantidade_parcelas',
            'cobranca_imediata', 'nome_contato_envio_nf', 'contato_envio_nf',
            'observacao', 'concluida', 'faturada', 'numero_nf', 'data_faturamento',
            'liberada_para_faturamento', 'data_atualizacao',
            'data_conclusao_os', 'finalizador_nome',
        ]
        read_only_fields = ['concluida', 'data_atualizacao', 'criado_por']

    def get_liberada_para_faturamento(self, obj):
        return obj.liberada_para_faturamento()

    def get_criado_por_nome(self, obj):
        if not obj.criado_por:
            return None
        return obj.criado_por.get_full_name() or obj.criado_por.username

    def get_data_conclusao_os(self, obj):
        ultimo_servico = obj.servicos.filter(status='concluida').order_by('-data_conclusao').first()
        if not ultimo_servico or not ultimo_servico.data_conclusao:
            return None
        return str(ultimo_servico.data_conclusao)

    def get_finalizador_nome(self, obj):
        ultimo_servico = obj.servicos.filter(status='concluida').order_by('-data_conclusao').first()
        if not ultimo_servico:
            return None
        ultima_tarefa = ultimo_servico.tarefas.filter(status='concluida').order_by('-atualizado_em').first()
        if not ultima_tarefa:
            return None
        return ultima_tarefa.responsavel.get_full_name() or ultima_tarefa.responsavel.username

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['criado_por'] = request.user
        return super().create(validated_data)
