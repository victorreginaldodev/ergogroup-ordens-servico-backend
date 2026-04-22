from rest_framework import serializers
from legado.ordemServico.models import Repositorio

class RepositorioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repositorio
        fields = '__all__'
