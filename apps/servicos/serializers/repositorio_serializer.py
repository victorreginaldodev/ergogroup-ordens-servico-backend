from rest_framework import serializers
from apps.servicos.models import Repositorio
from apps.servicos.serializers.subitem_repositorio_serializer import (
    SubitemRepositorioSerializer,
)


class RepositorioSerializer(serializers.ModelSerializer):
    subitens = SubitemRepositorioSerializer(many=True, read_only=True)

    class Meta:
        model = Repositorio
        fields = '__all__'
