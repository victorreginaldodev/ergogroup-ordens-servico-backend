from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.ordem_servico.models import OrdemServico
from apps.ordem_servico.serializers import OrdemServicoListSerializer, OrdemServicoSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar ordens de serviço',
        parameters=[
            OpenApiParameter('q', str, description='Busca por cliente ou observação'),
            OpenApiParameter('cliente', int, description='Filtrar por ID do cliente'),
            OpenApiParameter('concluida', str, description='Filtrar por conclusão (true/false)'),
            OpenApiParameter('faturada', str, description='Filtrar por faturamento (true/false)'),
        ],
    ),
    create=extend_schema(summary='Criar ordem de serviço'),
    retrieve=extend_schema(summary='Detalhar ordem de serviço'),
    update=extend_schema(summary='Atualizar ordem de serviço'),
    partial_update=extend_schema(summary='Atualizar ordem de serviço parcialmente'),
    destroy=extend_schema(summary='Remover ordem de serviço'),
)
class OrdemServicoViewSet(viewsets.ModelViewSet):
    queryset = OrdemServico.objects.select_related('cliente', 'criado_por').all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdemServicoListSerializer
        return OrdemServicoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        cliente_id = self.request.query_params.get('cliente', '').strip()
        concluida = self.request.query_params.get('concluida', '').strip()
        faturada = self.request.query_params.get('faturada', '').strip()

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

        return queryset

    @extend_schema(summary='Faturar ordem de serviço')
    @action(detail=True, methods=['patch'], url_path='faturar')
    def faturar(self, request, pk=None):
        os = self.get_object()
        if not os.liberada_para_faturamento():
            return Response(
                {'detail': 'Ordem de serviço não está liberada para faturamento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        numero_nf = request.data.get('numero_nf')
        data_faturamento = request.data.get('data_faturamento')
        os.faturada = True
        os.numero_nf = numero_nf
        os.data_faturamento = data_faturamento
        os.save(update_fields=['faturada', 'numero_nf', 'data_faturamento'])
        return Response(OrdemServicoSerializer(os, context={'request': request}).data)

    @extend_schema(summary='Verificar se está liberada para faturamento')
    @action(detail=True, methods=['get'], url_path='liberada-faturamento')
    def liberada_faturamento(self, request, pk=None):
        os = self.get_object()
        return Response({'liberada': os.liberada_para_faturamento()})
