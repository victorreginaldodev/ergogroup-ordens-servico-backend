from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.tarefas.models import RepositorioMiniOS
from apps.tarefas.serializers import RepositorioMiniOSSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar repositórios de Mini OS',
        description='Retorna o catálogo de serviços disponíveis para Mini OS. Suporta busca por nome ou descrição.',
        parameters=[OpenApiParameter('q', str, description='Busca por nome ou descrição (parcial).')],
    ),
    create=extend_schema(
        summary='Criar repositório de Mini OS',
        description='Cria um novo serviço no catálogo de Mini OS.',
    ),
    retrieve=extend_schema(
        summary='Detalhar repositório de Mini OS',
        description='Retorna todos os campos de um repositório de Mini OS pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar repositório de Mini OS',
        description='Substitui integralmente os dados de um repositório de Mini OS.',
    ),
    partial_update=extend_schema(
        summary='Atualizar repositório de Mini OS parcialmente',
        description='Atualiza um ou mais campos de um repositório de Mini OS.',
    ),
    destroy=extend_schema(
        summary='Remover repositório de Mini OS',
        description='Remove permanentemente um repositório de Mini OS.',
    ),
)
class RepositorioMiniOSViewSet(viewsets.ModelViewSet):
    queryset = RepositorioMiniOS.objects.all()
    serializer_class = RepositorioMiniOSSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(Q(nome__icontains=q) | Q(descricao__icontains=q))
        return queryset
