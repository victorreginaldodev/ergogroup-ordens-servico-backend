from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ordemServico.models import Tarefa, MiniOS
from ordemServico.serializers.TarefaMiniOSSerializer import TarefaMiniOSSerializer


class TarefaMiniOSAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tarefas = Tarefa.objects.select_related("servico", "profile").all()
        minios = MiniOS.objects.select_related("cliente", "servico", "profile").all()

        data = list(tarefas) + list(minios) 

        serializer = TarefaMiniOSSerializer(data, many=True)
        return Response(serializer.data)