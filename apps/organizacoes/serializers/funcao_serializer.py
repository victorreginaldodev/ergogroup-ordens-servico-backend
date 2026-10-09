from rest_framework import serializers

from apps.organizacoes.models import Funcao
from apps.organizacoes.permissoes import Permissao


class FuncaoSerializer(serializers.ModelSerializer):
    permissoes = serializers.ListField(
        child=serializers.ChoiceField(choices=Permissao.choices),
        source='codigos_permissao', required=False,
        help_text='Códigos das permissões que a função concede (ver permissoes-disponiveis).',
    )

    class Meta:
        model = Funcao
        fields = ['id', 'organizacao', 'nome', 'descricao', 'ativo', 'permissoes', 'criado_em', 'atualizado_em']
        read_only_fields = ['criado_em', 'atualizado_em']
        extra_kwargs = {'ativo': {'default': True}}

    def create(self, validated_data):
        codigos = validated_data.pop('codigos_permissao', [])
        funcao = super().create(validated_data)
        funcao.definir_permissoes(codigos)
        return funcao

    def update(self, instance, validated_data):
        codigos = validated_data.pop('codigos_permissao', None)
        funcao = super().update(instance, validated_data)
        if codigos is not None:
            funcao.definir_permissoes(codigos)
        return funcao


class PermissaoCatalogoSerializer(serializers.Serializer):
    codigo = serializers.CharField()
    descricao = serializers.CharField()
    escopo = serializers.ChoiceField(choices=['global', 'setor'])
