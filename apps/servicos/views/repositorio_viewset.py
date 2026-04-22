from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.servicos.models import Repositorio
from apps.servicos.serializers import RepositorioSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar repositórios',
        parameters=[OpenApiParameter('q', str, description='Busca por nome')],
    ),
    create=extend_schema(summary='Criar repositório'),
    retrieve=extend_schema(summary='Detalhar repositório'),
    update=extend_schema(summary='Atualizar repositório'),
    partial_update=extend_schema(summary='Atualizar repositório parcialmente'),
    destroy=extend_schema(summary='Remover repositório'),
)
class RepositorioViewSet(viewsets.ModelViewSet):
    queryset = Repositorio.objects.all()
    serializer_class = RepositorioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))
        return queryset
