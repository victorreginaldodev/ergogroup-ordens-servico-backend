from rest_framework import viewsets
from legado.ordemServico.models import MiniOS
from legado.ordemServico.serializers import MiniOSSerializer

class MiniOsViewSet(viewsets.ReadOnlyModelViewSet):  # Certifique-se de usar a classe correta
    queryset = MiniOS.objects.all()
    serializer_class = MiniOSSerializer
