from rest_framework import viewsets
from ordemServico.models import OrdemServico
from ordemServico.serializers import OrdemServicoSerializer

class OrdemServicoViewSet(viewsets.ReadOnlyModelViewSet): 
    queryset = OrdemServico.objects.all()
    serializer_class = OrdemServicoSerializer
