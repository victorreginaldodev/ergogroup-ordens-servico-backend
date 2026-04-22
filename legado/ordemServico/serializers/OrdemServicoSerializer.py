from django.db import transaction
from rest_framework import serializers
from legado.ordemServico.models import OrdemServico, Cliente, Servico, Repositorio, Tarefa, Profile


class ProfileOrdemServicoSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ['user_name', 'role']


class TarefaEmbeddedSerializer(serializers.ModelSerializer):
    profile = ProfileOrdemServicoSerializer()

    class Meta:
        model = Tarefa
        fields = ['data_inicio', 'data_termino', 'status', 'profile']


class RepositorioEmbeddedSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repositorio
        fields = ['nome']


class ServicoEmbeddedSerializer(serializers.ModelSerializer):
    tarefas = TarefaEmbeddedSerializer(many=True, read_only=True,)
    repositorio = RepositorioEmbeddedSerializer(read_only=True)
    repositorio_id = serializers.PrimaryKeyRelatedField(
        queryset=Repositorio.objects.all(), source='repositorio', write_only=True, required=True, allow_null=False
    )

    class Meta:
        model = Servico
        fields = ['id', 'repositorio', 'repositorio_id', 'descricao', 'tarefas', 'status', 'data_conclusao']
        read_only_fields = ['status', 'data_conclusao']


class ClienteOrdemServicoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = ['id', 'nome']


class OrdemServicoListSerializer(serializers.ModelSerializer):
    cliente = ClienteOrdemServicoSerializer(read_only=True)

    class Meta:
        model = OrdemServico
        fields = ['id', 'cliente', 'valor', 'concluida', 'faturamento', 'data_criacao']


class OrdemServicoFaturamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    numero_os = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = OrdemServico
        fields = [
            'id',
            'numero_os',
            'cliente_nome',
            'valor',
            'forma_pagamento',
            'quantidade_parcelas',
            'cobranca_imediata',
            'faturamento_1',
            'nome_contato_envio_nf',
            'contato_envio_nf',
            'observacao',
            'faturamento',
            'data_faturamento',
            'numero_nf',
            'concluida',
        ]


class OrdemServicoSerializer(serializers.ModelSerializer):
    servicos = ServicoEmbeddedSerializer(many=True)

    class Meta:
        model = OrdemServico
        fields = '__all__'
        read_only_fields = ['concluida']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.cliente:
            representation['cliente'] = ClienteOrdemServicoSerializer(instance.cliente).data
        return representation

    def create(self, validated_data):
        servicos_data = validated_data.pop('servicos', [])
        ordem_servico = OrdemServico.objects.create(**validated_data)
        
        for servico_data in servicos_data:
            Servico.objects.create(ordem_servico=ordem_servico, **servico_data)
            
        return ordem_servico

    def update(self, instance, validated_data):
        servicos_data = validated_data.pop('servicos', None)

        with transaction.atomic():
            instance = super().update(instance, validated_data)

            if servicos_data is not None:
                raw_servicos = self.initial_data.get('servicos', [])

                if not isinstance(raw_servicos, list):
                    raw_servicos = []

                existing_ids = set(instance.servicos.values_list('id', flat=True))
                kept_ids = set()

                for i, servico_data in enumerate(servicos_data):
                    item_id = None
                    if i < len(raw_servicos):
                        raw_item = raw_servicos[i]
                        if isinstance(raw_item, dict):
                            item_id = raw_item.get('id')

                    if item_id:
                        try:
                            item_id = int(item_id)
                            if item_id in existing_ids:
                                servico = Servico.objects.get(id=item_id, ordem_servico=instance)
                                for attr, value in servico_data.items():
                                    setattr(servico, attr, value)
                                servico.save()
                                kept_ids.add(item_id)
                                continue
                        except (ValueError, Servico.DoesNotExist):
                            pass

                    new_servico = Servico.objects.create(ordem_servico=instance, **servico_data)
                    kept_ids.add(new_servico.id)

                removed_services = instance.servicos.exclude(id__in=kept_ids)
                blocked_services = removed_services.filter(tarefas__isnull=False).distinct()
                if blocked_services.exists():
                    blocked_ids = list(blocked_services.values_list('id', flat=True))
                    raise serializers.ValidationError({
                        'servicos': (
                            'Nao e permitido remover servicos com tarefas relacionadas. '
                            f'Servicos afetados: {blocked_ids}.'
                        )
                    })

                removed_services.delete()

            return instance
