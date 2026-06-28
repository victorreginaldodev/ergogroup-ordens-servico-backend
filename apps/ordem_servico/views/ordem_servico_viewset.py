from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.ordem_servico.models import OrdemServico
from apps.ordem_servico.serializers import (
    OrdemServicoListSerializer,
    OrdemServicoSerializer,
    FaturarRequestSerializer,
    LiberadaFaturamentoSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary='Listar ordens de serviço',
        description=(
            'Retorna a lista paginada de ordens de serviço com campos resumidos, '
            'ordenadas por status de faturamento e data de criação. '
            'Suporta busca textual e filtragem por cliente, conclusão, faturamento e liberação.'
        ),
        parameters=[
            OpenApiParameter('q', str, description='Busca por nome do cliente ou observação (parcial).'),
            OpenApiParameter('cliente', int, description='Filtrar pelo ID do cliente.'),
            OpenApiParameter('concluida', str, description='Filtrar por conclusão.', enum=['true', 'false']),
            OpenApiParameter('faturada', str, description='Filtrar por status de faturamento.', enum=['true', 'false']),
            OpenApiParameter('liberada', str, description='Filtrar por liberação para faturamento.', enum=['true', 'false']),
        ],
    ),
    create=extend_schema(
        summary='Criar ordem de serviço',
        description=(
            'Cria uma nova ordem de serviço. O campo `criado_por` é preenchido '
            'automaticamente com o usuário autenticado. Se `cobranca_imediata=true`, '
            'a OS já é criada com `liberada_para_faturamento=true`.'
        ),
    ),
    retrieve=extend_schema(
        summary='Detalhar ordem de serviço',
        description='Retorna todos os campos de uma ordem de serviço pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar ordem de serviço',
        description=(
            'Substitui integralmente os dados de uma OS. '
            'Campos calculados (`status`, `concluida`, `liberada_para_faturamento`) '
            'são somente leitura e ignorados no body.'
        ),
    ),
    partial_update=extend_schema(
        summary='Atualizar ordem de serviço parcialmente',
        description=(
            'Atualiza um ou mais campos de uma OS. '
            'Campos calculados (`status`, `concluida`, `liberada_para_faturamento`) '
            'são somente leitura e ignorados no body.'
        ),
    ),
    destroy=extend_schema(
        summary='Remover ordem de serviço',
        description='Remove permanentemente uma ordem de serviço.',
    ),
)
class OrdemServicoViewSet(viewsets.ModelViewSet):
    queryset = OrdemServico.objects.select_related(
        'cliente',
        'criado_por',
        'atualizado_por',
        'liberada_para_faturamento_por',
        'faturada_por',
    ).prefetch_related('servicos__tarefas__responsavel').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdemServicoListSerializer
        return OrdemServicoSerializer

    def get_queryset(self):
        queryset = super().get_queryset().order_by('faturada', '-data_criacao')
        q = self.request.query_params.get('q', '').strip()
        cliente_id = self.request.query_params.get('cliente', '').strip()
        concluida = self.request.query_params.get('concluida', '').strip()
        faturada = self.request.query_params.get('faturada', '').strip()
        liberada = self.request.query_params.get('liberada', '').strip()

        if q:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=q) | Q(observacao__icontains=q)
            )
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if concluida in ('true', 'false'):
            queryset = queryset.filter(concluida=(concluida == 'true'))
        if faturada in ('true', 'false'):
            queryset = queryset.filter(faturada=(faturada == 'true'))
        if liberada in ('true', 'false'):
            queryset = queryset.filter(liberada_para_faturamento=(liberada == 'true'))

        return queryset

    @extend_schema(
        summary='Faturar ordem de serviço',
        description=(
            'Marca a OS como faturada, registrando número da NF, data e o usuário responsável. '
            'Retorna 400 se a OS não estiver liberada para faturamento.'
        ),
        request=FaturarRequestSerializer,
        responses={
            200: OrdemServicoSerializer,
            400: None,
        },
    )
    @action(detail=True, methods=['patch'], url_path='faturar')
    def faturar(self, request, pk=None):
        os = self.get_object()
        if not os.liberada_para_faturamento:
            return Response(
                {'detail': 'Ordem de serviço não está liberada para faturamento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        numero_nf = request.data.get('numero_nf')
        data_faturamento = request.data.get('data_faturamento')
        os.faturada = True
        os.numero_nf = numero_nf
        os.data_faturamento = data_faturamento
        os.faturada_por = request.user
        os.save(update_fields=['faturada', 'numero_nf', 'data_faturamento', 'faturada_por', 'data_atualizacao'])
        return Response(OrdemServicoSerializer(os, context={'request': request}).data)

    @extend_schema(
        summary='Verificar liberação para faturamento',
        description='Retorna o status de liberação para faturamento da OS, com data e responsável pela liberação.',
        responses={200: LiberadaFaturamentoSerializer},
    )
    @action(detail=True, methods=['get'], url_path='liberada-faturamento')
    def liberada_faturamento(self, request, pk=None):
        os = self.get_object()
        return Response({
            'liberada': os.liberada_para_faturamento,
            'liberada_em': os.liberada_para_faturamento_em,
            'liberada_por': os.liberada_para_faturamento_por_id,
        })
