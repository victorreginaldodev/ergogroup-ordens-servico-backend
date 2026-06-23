from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.contas.models.choices import TipoUsuario
from apps.tarefas.models import Tarefa
from apps.tarefas.serializers import TarefaListSerializer, TarefaSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar tarefas',
        parameters=[
            OpenApiParameter('servico', int, description='Filtrar por ID do serviço'),
            OpenApiParameter('responsavel', int, description='Filtrar por ID do responsável'),
            OpenApiParameter('status', str, description='Filtrar por status (aberta/em_andamento/concluida/cancelada)'),
        ],
    ),
    create=extend_schema(summary='Criar tarefa'),
    retrieve=extend_schema(summary='Detalhar tarefa'),
    update=extend_schema(summary='Atualizar tarefa'),
    partial_update=extend_schema(summary='Atualizar tarefa parcialmente'),
    destroy=extend_schema(summary='Remover tarefa'),
)
class TarefaViewSet(viewsets.ModelViewSet):
    queryset = Tarefa.objects.select_related(
        'responsavel',
        'servico__repositorio',
        'servico__ordem_servico__cliente',
    ).all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return TarefaListSerializer
        return TarefaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.tipo_usuario == TipoUsuario.TECNICO:
            queryset = queryset.filter(responsavel=user)

        servico_id = self.request.query_params.get('servico', '').strip()
        responsavel_id = self.request.query_params.get('responsavel', '').strip()
        status_param = self.request.query_params.get('status', '').strip()

        if servico_id:
            queryset = queryset.filter(servico_id=servico_id)
        if responsavel_id:
            queryset = queryset.filter(responsavel_id=responsavel_id)
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset
