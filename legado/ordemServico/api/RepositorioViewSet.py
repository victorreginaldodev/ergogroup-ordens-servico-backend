from django.db.models import Q
from rest_framework import viewsets

from legado.ordemServico.models import Repositorio
from legado.ordemServico.serializers.RepositorioSerializer import RepositorioSerializer

from .pagination import OptionalPageNumberPagination


class RepositorioViewSet(viewsets.ModelViewSet):
    queryset = Repositorio.objects.all()
    serializer_class = RepositorioSerializer
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(descricao__icontains=q)
            )
        return queryset
