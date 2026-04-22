from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.clientes.models import Cliente
from apps.clientes.serializers import ClienteListSerializer, ClienteSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar clientes',
        parameters=[
            OpenApiParameter('q', str, description='Busca por nome ou número de inscrição'),
            OpenApiParameter('tipo', str, description='Filtrar por tipo de cliente'),
            OpenApiParameter('ativo', str, description='Filtrar por status (true/false)'),
        ],
    ),
    create=extend_schema(summary='Cadastrar cliente'),
    retrieve=extend_schema(summary='Detalhar cliente'),
    update=extend_schema(summary='Atualizar cliente'),
    partial_update=extend_schema(summary='Atualizar cliente parcialmente'),
    destroy=extend_schema(summary='Remover cliente'),
)
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ClienteListSerializer
        return ClienteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        tipo = self.request.query_params.get('tipo', '').strip()
        ativo = self.request.query_params.get('ativo', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(numero_inscricao__icontains=q)
            )
        if tipo:
            queryset = queryset.filter(tipo_cliente=tipo)
        if ativo in ('true', 'false'):
            queryset = queryset.filter(ativo=(ativo == 'true'))

        return queryset
