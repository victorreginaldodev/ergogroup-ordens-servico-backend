from rest_framework import serializers
from apps.catalogo.models import Catalogo
from apps.catalogo.serializers.subitem_catalogo_serializer import (
    SubitemCatalogoSerializer,
)


class CatalogoSerializer(serializers.ModelSerializer):
    subitens = SubitemCatalogoSerializer(many=True, read_only=True)

    class Meta:
        model = Catalogo
        fields = '__all__'
