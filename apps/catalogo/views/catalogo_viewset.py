from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.catalogo.models import Catalogo
from apps.catalogo.serializers import CatalogoSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar catálogos',
        description='Retorna a lista de catálogos com seus subitens. Suporta busca por nome ou descrição.',
        parameters=[OpenApiParameter('q', str, description='Busca por nome ou descrição (parcial).')],
    ),
    create=extend_schema(
        summary='Criar catálogo',
        description='Cria um novo catálogo.',
    ),
    retrieve=extend_schema(
        summary='Detalhar catálogo',
        description='Retorna todos os campos de um catálogo, incluindo seus subitens.',
    ),
    update=extend_schema(
        summary='Atualizar catálogo',
        description='Substitui integralmente os dados de um catálogo.',
    ),
    partial_update=extend_schema(
        summary='Atualizar catálogo parcialmente',
        description='Atualiza um ou mais campos de um catálogo.',
    ),
    destroy=extend_schema(
        summary='Remover catálogo',
        description='Remove permanentemente um catálogo e todos os seus subitens.',
    ),
)
class CatalogoViewSet(viewsets.ModelViewSet):
    queryset = Catalogo.objects.prefetch_related('subitens').all()
    serializer_class = CatalogoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))
        return queryset
