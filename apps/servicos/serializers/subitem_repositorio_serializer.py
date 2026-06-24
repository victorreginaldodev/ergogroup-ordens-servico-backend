from rest_framework import serializers

from apps.servicos.models import SubitemRepositorio


class SubitemRepositorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubitemRepositorio
        fields = '__all__'
        read_only_fields = ['criado_em', 'atualizado_em']
