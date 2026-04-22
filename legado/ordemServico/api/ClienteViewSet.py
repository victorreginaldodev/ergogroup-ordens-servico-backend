from django.db.models import Q
from rest_framework import viewsets

from legado.ordemServico.models import Cliente
from legado.ordemServico.serializers.ClienteSerializer import ClienteSerializer

from .pagination import OptionalPageNumberPagination


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset().order_by('nome')
        q = self.request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nome__icontains=q)
                | Q(numero_inscricao__icontains=q)
                | Q(nome_representante__icontains=q)
            )
        return queryset
