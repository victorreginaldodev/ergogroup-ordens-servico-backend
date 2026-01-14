from rest_framework import viewsets
from ordemServico.models import Tarefa
from ordemServico.serializers.TarefaSerializer import TarefaSerializer, TarefaListSerializer, TarefaDetailSerializer

class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Tarefa.objects.all()
        
        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role == 5: # Técnico
                queryset = queryset.filter(profile__user=user)
            elif user.profile.role == 6: # Gestor Comercial
                # Mesma regra do técnico: vê apenas suas próprias tarefas
                queryset = queryset.filter(profile__user=user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TarefaListSerializer
        if self.action == 'retrieve':
            return TarefaDetailSerializer
        return TarefaSerializer
