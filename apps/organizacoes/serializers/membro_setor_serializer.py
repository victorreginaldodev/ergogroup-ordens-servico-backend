from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.organizacoes.models import MembroSetor


class MembroSetorSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome_completo', read_only=True)
    setor_nome = serializers.CharField(source='setor.nome', read_only=True)
    funcao_nome = serializers.CharField(source='funcao.nome', read_only=True)

    class Meta:
        model = MembroSetor
        fields = [
            'id', 'usuario', 'usuario_nome', 'setor', 'setor_nome', 'funcao', 'funcao_nome',
            'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['criado_em', 'atualizado_em']

    def validate(self, attrs):
        atuais = {}
        if self.instance is not None:
            atuais = {'usuario': self.instance.usuario, 'setor': self.instance.setor, 'funcao': self.instance.funcao}
        try:
            MembroSetor(**{**atuais, **attrs}).clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        return attrs
