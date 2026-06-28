from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.servicos.models import Repositorio
from apps.servicos.serializers import RepositorioSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar repositórios',
        description='Retorna a lista de repositórios com seus subitens. Suporta busca por nome ou descrição.',
        parameters=[OpenApiParameter('q', str, description='Busca por nome ou descrição (parcial).')],
    ),
    create=extend_schema(
        summary='Criar repositório',
        description='Cria um novo repositório.',
    ),
    retrieve=extend_schema(
        summary='Detalhar repositório',
        description='Retorna todos os campos de um repositório, incluindo seus subitens.',
    ),
    update=extend_schema(
        summary='Atualizar repositório',
        description='Substitui integralmente os dados de um repositório.',
    ),
    partial_update=extend_schema(
        summary='Atualizar repositório parcialmente',
        description='Atualiza um ou mais campos de um repositório.',
    ),
    destroy=extend_schema(
        summary='Remover repositório',
        description='Remove permanentemente um repositório e todos os seus subitens.',
    ),
)
class RepositorioViewSet(viewsets.ModelViewSet):
    queryset = Repositorio.objects.prefetch_related('subitens').all()
    serializer_class = RepositorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))
        return queryset
