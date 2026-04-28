from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
    queryset = MiniOS.objects.select_related('cliente', 'servico', 'responsavel').all()
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
