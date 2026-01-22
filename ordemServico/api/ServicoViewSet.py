from rest_framework import viewsets
from django.db.models import Exists, OuterRef
from ordemServico.models import Servico, Tarefa
from ordemServico.serializers.ServicoSerializer import ServicoSerializer, ServicoListSerializer

class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.annotate(
                has_tarefas=Exists(Tarefa.objects.filter(servico=OuterRef('pk')))
            )
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        return ServicoSerializer
