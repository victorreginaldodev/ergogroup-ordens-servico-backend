from rest_framework import serializers
from apps.ordem_servico.models import OrdemServico
from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteListSerializer, ClienteSerializer


class OrdemServicoListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'cliente', 'cliente_nome', 'data_criacao', 'valor',
            'forma_pagamento', 'forma_pagamento_display', 'status',
            'status_display', 'prioridade', 'prioridade_display',
            'concluida', 'faturada', 'cobranca_imediata', 'contrato',
            'liberada_para_faturamento', 'liberada_para_faturamento_em',
        ]


class OrdemServicoSerializer(serializers.ModelSerializer):
    cliente_detail = ClienteSerializer(source='cliente', read_only=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    forma_pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    criado_por_nome = serializers.SerializerMethodField()
    liberada_para_faturamento_por_nome = serializers.SerializerMethodField()
    faturada_por_nome = serializers.SerializerMethodField()
    data_conclusao_os = serializers.SerializerMethodField()
    finalizador_nome = serializers.SerializerMethodField()

    class Meta:
        model = OrdemServico
        fields = [
            'id', 'cliente', 'cliente_detail',
            'criado_por', 'criado_por_nome', 'data_criacao', 'criada_em',
            'status', 'status_display', 'prioridade', 'prioridade_display', 'valor',
            'forma_pagamento', 'forma_pagamento_display', 'quantidade_parcelas',
            'cobranca_imediata', 'nome_contato_envio_nf', 'contato_envio_nf',
            'contrato', 'objeto_contrato', 'contrato_data_inicio',
            'contrato_data_fim', 'gestor_contrato_nome',
            'gestor_contrato_email', 'gestor_contrato_telefone',
            'observacao', 'concluida', 'faturada', 'numero_nf', 'data_faturamento',
            'faturada_por', 'faturada_por_nome',
            'liberada_para_faturamento', 'liberada_para_faturamento_em',
            'liberada_para_faturamento_por', 'liberada_para_faturamento_por_nome',
            'data_atualizacao', 'atualizado_por',
            'data_conclusao_os', 'finalizador_nome',
        ]
        read_only_fields = [
            'status', 'concluida', 'criada_em', 'data_atualizacao',
            'criado_por', 'atualizado_por', 'liberada_para_faturamento',
            'liberada_para_faturamento_em', 'liberada_para_faturamento_por',
            'faturada_por',
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        contrato = attrs.get('contrato', getattr(self.instance, 'contrato', False))

        if contrato:
            campos_obrigatorios = {
                'objeto_contrato': 'Informe o objeto do contrato.',
                'contrato_data_inicio': 'Informe a data de início do contrato.',
                'contrato_data_fim': 'Informe a data de fim do contrato.',
            }
            erros = {}
            for campo, mensagem in campos_obrigatorios.items():
                valor = attrs.get(campo, getattr(self.instance, campo, None))
                if not valor:
                    erros[campo] = mensagem

            data_inicio = attrs.get('contrato_data_inicio', getattr(self.instance, 'contrato_data_inicio', None))
            data_fim = attrs.get('contrato_data_fim', getattr(self.instance, 'contrato_data_fim', None))
            if data_inicio and data_fim and data_fim < data_inicio:
                erros['contrato_data_fim'] = 'A data de fim não pode ser anterior à data de início.'

            if erros:
                raise serializers.ValidationError(erros)

        return attrs

    def get_criado_por_nome(self, obj):
        if not obj.criado_por:
            return None
        return obj.criado_por.nome_completo or obj.criado_por.get_full_name() or obj.criado_por.username

    def get_liberada_para_faturamento_por_nome(self, obj):
        if not obj.liberada_para_faturamento_por:
            return None
        usuario = obj.liberada_para_faturamento_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def get_faturada_por_nome(self, obj):
        if not obj.faturada_por:
            return None
        usuario = obj.faturada_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def get_data_conclusao_os(self, obj):
        ultimo_servico = obj.servicos.filter(status='concluida').order_by('-data_termino', '-data_conclusao', '-id').first()
        if not ultimo_servico:
            return None
        data_conclusao = ultimo_servico.data_termino or ultimo_servico.data_conclusao
        return str(data_conclusao) if data_conclusao else None

    def get_finalizador_nome(self, obj):
        if obj.liberada_para_faturamento_por:
            usuario = obj.liberada_para_faturamento_por
            return usuario.nome_completo or usuario.get_full_name() or usuario.username
        ultimo_servico = obj.servicos.filter(status='concluida').order_by('-data_termino', '-data_conclusao', '-id').first()
        if not ultimo_servico or not ultimo_servico.terminado_por:
            return None
        usuario = ultimo_servico.terminado_por
        return usuario.nome_completo or usuario.get_full_name() or usuario.username

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['criado_por'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['atualizado_por'] = request.user
            if validated_data.get('faturada') is True and not instance.faturada:
                validated_data['faturada_por'] = request.user
        return super().update(instance, validated_data)
