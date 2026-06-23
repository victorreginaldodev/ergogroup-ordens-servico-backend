from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.servicos.models import Servico
from apps.servicos.serializers import ServicoListSerializer, ServicoSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar serviços',
        parameters=[
            OpenApiParameter('ordem_servico', int, description='Filtrar por ID da ordem de serviço'),
            OpenApiParameter('status', str, description='Filtrar por status (aberto/em_andamento/concluida/cancelado)'),
            OpenApiParameter('repositorio', int, description='Filtrar por ID do repositório'),
        ],
    ),
    create=extend_schema(summary='Criar serviço'),
    retrieve=extend_schema(summary='Detalhar serviço'),
    update=extend_schema(summary='Atualizar serviço'),
    partial_update=extend_schema(summary='Atualizar serviço parcialmente'),
    destroy=extend_schema(summary='Remover serviço'),
)
class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.select_related(
        'ordem_servico__cliente',
        'repositorio',
        'terminado_por',
    ).prefetch_related('tarefas').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ServicoListSerializer
        return ServicoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        ordem_id = self.request.query_params.get('ordem_servico', '').strip()
        status_param = self.request.query_params.get('status', '').strip()
        repositorio_id = self.request.query_params.get('repositorio', '').strip()

        if ordem_id:
            queryset = queryset.filter(ordem_servico_id=ordem_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if repositorio_id:
            queryset = queryset.filter(repositorio_id=repositorio_id)

        return queryset

    @extend_schema(summary='Sincronizar status com base nas tarefas')
    @action(detail=True, methods=['post'], url_path='sincronizar')
    def sincronizar(self, request, pk=None):
        servico = self.get_object()
        servico.sincronizar_status_e_rastreio()
        return Response(ServicoSerializer(servico, context={'request': request}).data)
