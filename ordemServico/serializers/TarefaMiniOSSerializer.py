from rest_framework import serializers
from ordemServico.models import Tarefa, MiniOS

class TarefaMiniOSSerializer(serializers.Serializer):
    cliente = serializers.CharField(source="cliente.nome", allow_null=True)
    servico = serializers.CharField(source="servico.nome", allow_null=True)
    profile = serializers.CharField(source="profile.user.username", allow_null=True)
    data_inicio = serializers.DateField(allow_null=True)
    data_termino = serializers.DateField(allow_null=True)
    status = serializers.CharField()

    def to_representation(self, instance):
        """ Formata os dados corretamente, independentemente do modelo de origem """
        if isinstance(instance, Tarefa):
            return {
                "cliente": instance.servico.ordem_servico.cliente.nome if instance.servico.ordem_servico and instance.servico.ordem_servico.cliente else "Sem Cliente",
                "servico": instance.servico.repositorio.nome if instance.servico.repositorio else "Sem Serviço",
                "profile": instance.profile.user.username if instance.profile else "Sem Profile",
                "data_inicio": instance.data_inicio,
                "data_termino": instance.data_termino,
                "status": instance.status,
            }
        elif isinstance(instance, MiniOS):
            return {
                "cliente": instance.cliente.nome if instance.cliente else "Sem Cliente",
                "servico": instance.servico.nome if instance.servico else "Sem Serviço",
                "profile": instance.profile.user.username if instance.profile else "Sem Profile",
                "data_inicio": instance.data_inicio,
                "data_termino": instance.data_termino,
                "status": instance.status,
            }
        return super().to_representation(instance)