from django.db.models import Q
from rest_framework import viewsets

from legado.ordemServico.models import RepositorioMiniOS
from legado.ordemServico.serializers.RepositorioMiniOSSerializer import RepositorioMiniOSSerializer

from .pagination import OptionalPageNumberPagination


class RepositorioMiniOSViewSet(viewsets.ModelViewSet):
    queryset = RepositorioMiniOS.objects.all()
    serializer_class = RepositorioMiniOSSerializer
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q) | Q(descricao__icontains=q)
            )
        return queryset
