from django.db.models import Q
from rest_framework import viewsets

from legado.ordemServico.models import Tarefa
from legado.ordemServico.serializers.TarefaSerializer import (
    TarefaDetailSerializer,
    TarefaListSerializer,
    TarefaSerializer,
)

from .pagination import OptionalPageNumberPagination


class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Tarefa.objects.all()

        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role == 5:
                queryset = queryset.filter(profile__user=user)
            elif user.profile.role == 6:
                queryset = queryset.filter(profile__user=user)

        if self.action == 'list':
            q = self.request.query_params.get('q', '').strip()
            status = self.request.query_params.get('status', '').strip()

            if q:
                queryset = queryset.filter(
                    Q(servico__ordem_servico__cliente__nome__icontains=q)
                    | Q(servico__repositorio__nome__icontains=q)
                    | Q(profile__user__username__icontains=q)
                    | Q(descricao__icontains=q)
                )

            if status:
                status_map = {
                    'pending': 'nao_iniciada',
                    'in_progress': 'em_andamento',
                    'completed': 'concluida',
                }
                queryset = queryset.filter(status=status_map.get(status, status))

            queryset = queryset.select_related(
                'profile__user',
                'servico__repositorio',
                'servico__ordem_servico__cliente',
            ).order_by('status', '-id')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return TarefaListSerializer
        if self.action == 'retrieve':
            return TarefaDetailSerializer
        return TarefaSerializer
