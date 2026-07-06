from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.ordens_servico.models import Servico, Prioridade
from apps.ordens_servico.models.servico import StatusServico
from apps.ordens_servico.serializers import ServicoListSerializer, ServicoSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar serviços',
        description=(
            'Retorna a lista paginada de serviços com campos resumidos. '
            'Suporta filtragem por OS, status e catálogo.'
        ),
        parameters=[
            OpenApiParameter('ordem_servico', int, description='Filtrar pelo ID da ordem de serviço.'),
            OpenApiParameter('status', str, description='Filtrar por status.', enum=StatusServico),
            OpenApiParameter('catalogo', int, description='Filtrar pelo ID do catálogo.'),
            OpenApiParameter('prioridade', str, description='Filtrar por prioridade.', enum=Prioridade),
            OpenApiParameter('atrasada', str, description='Se "true", retorna apenas serviços com prazo vencido e não concluídos/cancelados.', enum=['true']),
            OpenApiParameter('ordering', str, description='Ordenar por prazo. Use "prazo" ou "-prazo".', enum=['prazo', '-prazo']),
        ],
    ),
    create=extend_schema(
        summary='Criar serviço',
        description=(
            'Cria um novo serviço vinculado a uma OS. '
            'Campos calculados (`status`, `data_inicio`, `data_termino`, `data_conclusao`, '
            '`terminado_por`) são somente leitura e gerenciados automaticamente pelas tarefas.'
        ),
    ),
    retrieve=extend_schema(
        summary='Detalhar serviço',
        description='Retorna todos os campos de um serviço pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar serviço',
        description=(
            'Substitui integralmente os dados de um serviço. '
            'Campos calculados são somente leitura e ignorados no body.'
        ),
    ),
    partial_update=extend_schema(
        summary='Atualizar serviço parcialmente',
        description=(
            'Atualiza um ou mais campos de um serviço. '
            'Campos calculados são somente leitura e ignorados no body.'
        ),
    ),
    destroy=extend_schema(
        summary='Remover serviço',
        description='Remove permanentemente um serviço e suas tarefas vinculadas.',
    ),
)
class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.select_related(
        'ordem_servico__cliente',
        'catalogo',
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
        catalogo_id = self.request.query_params.get('catalogo', '').strip()
        prioridade_param = self.request.query_params.get('prioridade', '').strip()
        atrasada_param = self.request.query_params.get('atrasada', '').strip()
        ordering_param = self.request.query_params.get('ordering', '').strip()

        if ordem_id:
            queryset = queryset.filter(ordem_servico_id=ordem_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if catalogo_id:
            queryset = queryset.filter(catalogo_id=catalogo_id)
        if prioridade_param:
            queryset = queryset.filter(prioridade=prioridade_param)
        if atrasada_param == 'true':
            queryset = queryset.filter(prazo__lt=timezone.localdate()).exclude(
                status__in=[StatusServico.CONCLUIDA, StatusServico.CANCELADO]
            )
        if ordering_param in ('prazo', '-prazo'):
            queryset = queryset.order_by(ordering_param)

        return queryset

    @extend_schema(
        summary='Sincronizar status do serviço',
        description=(
            'Força a ressincronização do status, datas e responsável do serviço '
            'com base no estado atual de suas tarefas. '
            'Normalmente executado automaticamente por signals — use este endpoint '
            'apenas para corrigir inconsistências manualmente.'
        ),
        request=None,
        responses={200: ServicoSerializer},
    )
    @action(detail=True, methods=['post'], url_path='sincronizar')
    def sincronizar(self, request, pk=None):
        servico = self.get_object()
        servico.sincronizar_status_e_rastreio()
        return Response(ServicoSerializer(servico, context={'request': request}).data)
