from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.contas.models.choices import TipoUsuario
from apps.tarefas.models import MiniOS
from apps.tarefas.serializers import MiniOSListSerializer, MiniOSSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar Mini OS',
        parameters=[
            OpenApiParameter('q', str, description='Busca por cliente ou serviço'),
            OpenApiParameter('cliente', int, description='Filtrar por ID do cliente'),
            OpenApiParameter('responsavel', int, description='Filtrar por ID do responsável'),
            OpenApiParameter('status', str, description='Filtrar por status'),
            OpenApiParameter('faturada', str, description='Filtrar por faturamento (true/false)'),
        ],
    ),
    create=extend_schema(summary='Criar Mini OS'),
    retrieve=extend_schema(summary='Detalhar Mini OS'),
    update=extend_schema(summary='Atualizar Mini OS'),
    partial_update=extend_schema(summary='Atualizar Mini OS parcialmente'),
    destroy=extend_schema(summary='Remover Mini OS'),
)
class MiniOSViewSet(viewsets.ModelViewSet):
    queryset = MiniOS.objects.select_related(
        'cliente',
        'servico',
        'responsavel',
        'liberada_cobranca_por',
        'faturada_por',
    ).all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MiniOSListSerializer
        return MiniOSSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.tipo_usuario == TipoUsuario.TECNICO:
            queryset = queryset.filter(responsavel=user)

        q = self.request.query_params.get('q', '').strip()
        cliente_id = self.request.query_params.get('cliente', '').strip()
        responsavel_id = self.request.query_params.get('responsavel', '').strip()
        status_param = self.request.query_params.get('status', '').strip()
        faturada = self.request.query_params.get('faturada', '').strip()

        if q:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=q) | Q(servico__nome__icontains=q)
            )
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if responsavel_id:
            queryset = queryset.filter(responsavel_id=responsavel_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if faturada in ('true', 'false'):
            queryset = queryset.filter(faturada=(faturada == 'true'))

        return queryset

    @extend_schema(summary='Faturar Mini OS')
    @action(detail=True, methods=['patch'], url_path='faturar')
    def faturar(self, request, pk=None):
        mini_os = self.get_object()
        if not mini_os.gera_cobranca:
            return Response(
                {'detail': 'Mini OS não gera cobrança.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if mini_os.data_liberacao_cobranca is None:
            return Response(
                {'detail': 'Mini OS ainda não está liberada para cobrança.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        numero_nf = request.data.get('numero_nf')
        mini_os.faturada = True
        mini_os.numero_nf = numero_nf
        mini_os.faturada_por = request.user
        mini_os.save(update_fields=['faturada', 'numero_nf', 'faturada_por', 'atualizado_em'])
        return Response(MiniOSSerializer(mini_os, context={'request': request}).data)
