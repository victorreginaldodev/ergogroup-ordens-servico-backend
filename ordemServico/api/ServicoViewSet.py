from django.db.models import Exists, OuterRef, Q
from rest_framework import viewsets

from ordemServico.models import Servico, Tarefa
from ordemServico.serializers.ServicoSerializer import (
    ServicoListSerializer,
    ServicoSerializer,
)

from .pagination import OptionalPageNumberPagination


class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            queryset = queryset.annotate(
                has_tarefas=Exists(Tarefa.objects.filter(servico=OuterRef('pk')))
            )

            q = self.request.query_params.get('q', '').strip()
            status = self.request.query_params.get('status', '').strip()
            has_tasks = self.request.query_params.get('has_tasks', '').strip()

            if q:
                queryset = queryset.filter(
                    Q(repositorio__nome__icontains=q)
                    | Q(ordem_servico__cliente__nome__icontains=q)
                    | Q(descricao__icontains=q)
                )

            if status:
                status_map = {
                    'pending': 'em_espera',
                    'in_progress': 'em_andamento',
                    'completed': 'concluida',
                }
                queryset = queryset.filter(status=status_map.get(status, status))

            if has_tasks == 'true':
                queryset = queryset.filter(has_tarefas=True)
            elif has_tasks == 'false':
                queryset = queryset.filter(has_tarefas=False)

            queryset = queryset.select_related(
                'repositorio',
                'ordem_servico__cliente',
            ).order_by('status', '-id')
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        return ServicoSerializer
