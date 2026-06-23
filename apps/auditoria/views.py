from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.auditoria.models import RegistroAuditoria
from apps.auditoria.serializers import RegistroAuditoriaSerializer


class RegistroAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistroAuditoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = RegistroAuditoria.objects.select_related('usuario').all()
        filtros = {
            'entidade': 'entidade',
            'objeto_id': 'objeto_id',
            'acao': 'acao',
            'ordem_servico': 'ordem_servico_id',
            'servico': 'servico_id',
            'tarefa': 'tarefa_id',
            'mini_os': 'mini_os_id',
        }
        for param, campo in filtros.items():
            valor = self.request.query_params.get(param)
            if valor:
                queryset = queryset.filter(**{campo: valor})
        return queryset

    @action(detail=False, methods=['get'], url_path='ordens/(?P<ordem_servico_id>[^/.]+)/timeline')
    def timeline_ordem(self, request, ordem_servico_id=None):
        queryset = self.get_queryset().filter(ordem_servico_id=ordem_servico_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='mini-os/(?P<mini_os_id>[^/.]+)/timeline')
    def timeline_mini_os(self, request, mini_os_id=None):
        queryset = self.get_queryset().filter(mini_os_id=mini_os_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
