from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ordemServico.models import Tarefa, MiniOS
from ordemServico.serializers.TarefaMiniOSSerializer import TarefaMiniOSSerializer


class TarefaMiniOSAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        tarefas = Tarefa.objects.select_related("servico", "profile").all()
        minios = MiniOS.objects.select_related("cliente", "servico", "profile").all()

        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role == 5: # Técnico
                tarefas = tarefas.filter(profile__user=user)
                minios = minios.filter(profile__user=user)
            elif user.profile.role == 6: # Gestor Comercial
                # Mesma regra do técnico: vê apenas suas próprias tarefas e minios
                tarefas = tarefas.filter(profile__user=user)
                minios = minios.filter(profile__user=user)

        data = list(tarefas) + list(minios) 

        serializer = TarefaMiniOSSerializer(data, many=True)
        return Response(serializer.data)