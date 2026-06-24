from django.db.models import Q
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.servicos.models import SubitemRepositorio
from apps.servicos.serializers import SubitemRepositorioSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar subitens de repositorio',
        parameters=[
            OpenApiParameter('repositorio', int, description='Filtra por repositorio'),
            OpenApiParameter('ativo', bool, description='Filtra por status ativo'),
            OpenApiParameter('q', str, description='Busca por nome ou descricao'),
        ],
    ),
    create=extend_schema(summary='Criar subitem de repositorio'),
    retrieve=extend_schema(summary='Detalhar subitem de repositorio'),
    update=extend_schema(summary='Atualizar subitem de repositorio'),
    partial_update=extend_schema(summary='Atualizar subitem de repositorio parcialmente'),
    destroy=extend_schema(summary='Remover subitem de repositorio'),
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
