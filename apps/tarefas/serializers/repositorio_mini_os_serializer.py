from rest_framework import serializers
from apps.tarefas.models import RepositorioMiniOS


class RepositorioMiniOSSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositorioMiniOS
        fields = '__all__'
