from rest_framework import serializers
from apps.ordem_servico.models import OrdemServico
from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteListSerializer


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
    cliente_detail = ClienteListSerializer(source='cliente', read_only=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    liberada_para_faturamento = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'cliente', 'cliente_detail',
            'criado_por', 'data_criacao', 'valor',
            'forma_pagamento', 'forma_pagamento_display', 'quantidade_parcelas',
            'cobranca_imediata', 'nome_contato_envio_nf', 'contato_envio_nf',
            'observacao', 'concluida', 'faturada', 'numero_nf', 'data_faturamento',
            'liberada_para_faturamento', 'data_atualizacao',
        ]
        read_only_fields = ['concluida', 'data_atualizacao', 'criado_por']

    def get_liberada_para_faturamento(self, obj):
        return obj.liberada_para_faturamento()

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['criado_por'] = request.user
        return super().create(validated_data)
