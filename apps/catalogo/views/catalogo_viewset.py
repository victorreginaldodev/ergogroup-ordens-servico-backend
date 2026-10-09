from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.catalogo.models import Catalogo
from apps.catalogo.serializers import CatalogoSerializer
from apps.organizacoes.permissoes import Permissao, PermissoesPorAcaoMixin


@extend_schema_view(
    list=extend_schema(
        summary='Listar catálogos',
        description='Retorna a lista de catálogos com seus subitens. Suporta busca por nome ou descrição e filtro por setor.',
        parameters=[
            OpenApiParameter('q', str, description='Busca por nome ou descrição (parcial).'),
            OpenApiParameter('setor', int, description='Filtrar pelo ID do setor.'),
        ],
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
        description=(
            'Remove permanentemente um catálogo e todos os seus subitens. '
            'Retorna 409 se o catálogo estiver vinculado a serviços.'
        ),
    ),
)
class CatalogoViewSet(PermissoesPorAcaoMixin, viewsets.ModelViewSet):
    queryset = Catalogo.objects.prefetch_related('subitens').all()
    serializer_class = CatalogoSerializer
    permission_classes = [IsAuthenticated]
    permissoes_por_acao = {
        'create': (Permissao.CATALOGO_GERENCIAR,),
        'update': (Permissao.CATALOGO_GERENCIAR,),
        'partial_update': (Permissao.CATALOGO_GERENCIAR,),
        'destroy': (Permissao.CATALOGO_GERENCIAR,),
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        setor_id = self.request.query_params.get('setor', '').strip()
        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))
        if setor_id:
            queryset = queryset.filter(setor_id=setor_id)
        return queryset
