from rest_framework import serializers
from apps.organizacoes.models import Setor


class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setor
        fields = ['id', 'organizacao', 'nome', 'descricao', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['criado_em', 'atualizado_em']
        # Sem default explícito, o DRF trata booleano ausente em form/multipart como False.
        extra_kwargs = {'ativo': {'default': True}}
