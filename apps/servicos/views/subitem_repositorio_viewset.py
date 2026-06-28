from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.servicos.models import SubitemRepositorio
from apps.servicos.serializers import SubitemRepositorioSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar subitens de repositório',
        description='Retorna a lista de subitens de repositório. Suporta filtragem por repositório, status e busca textual.',
        parameters=[
            OpenApiParameter('repositorio', int, description='Filtrar pelo ID do repositório.'),
            OpenApiParameter('ativo', str, description='Filtrar por status de ativação.', enum=['true', 'false']),
            OpenApiParameter('q', str, description='Busca por nome ou descrição (parcial).'),
        ],
    ),
    create=extend_schema(
        summary='Criar subitem de repositório',
        description='Cria um novo subitem vinculado a um repositório. O par (repositório, nome) deve ser único.',
    ),
    retrieve=extend_schema(
        summary='Detalhar subitem de repositório',
        description='Retorna todos os campos de um subitem de repositório pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar subitem de repositório',
        description='Substitui integralmente os dados de um subitem de repositório.',
    ),
    partial_update=extend_schema(
        summary='Atualizar subitem de repositório parcialmente',
        description='Atualiza um ou mais campos de um subitem de repositório.',
    ),
    destroy=extend_schema(
        summary='Remover subitem de repositório',
        description='Remove permanentemente um subitem de repositório.',
    ),
)
class SubitemRepositorioViewSet(viewsets.ModelViewSet):
    queryset = SubitemRepositorio.objects.select_related('repositorio').all()
    serializer_class = SubitemRepositorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        repositorio = self.request.query_params.get('repositorio')
        ativo = self.request.query_params.get('ativo')
        q = self.request.query_params.get('q', '').strip()

        if repositorio:
            queryset = queryset.filter(repositorio_id=repositorio)

        if ativo is not None:
            ativo_normalizado = ativo.strip().lower()
            if ativo_normalizado in ['true', '1', 'sim']:
                queryset = queryset.filter(ativo=True)
            elif ativo_normalizado in ['false', '0', 'nao']:
                queryset = queryset.filter(ativo=False)

        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))

        return queryset
