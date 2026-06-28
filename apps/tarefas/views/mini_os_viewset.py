from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.contas.models.choices import TipoUsuario
from apps.tarefas.models import MiniOS
from apps.tarefas.models.mini_os import StatusMiniOS
from apps.tarefas.serializers import MiniOSListSerializer, MiniOSSerializer, FaturarMiniOSRequestSerializer


@extend_schema_view(
    list=extend_schema(
        summary='Listar Mini OS',
        description=(
            'Retorna a lista paginada de Mini OS. '
            'Técnicos veem apenas as próprias Mini OS; demais perfis veem todas.'
        ),
        parameters=[
            OpenApiParameter('q', str, description='Busca por nome do cliente ou serviço (parcial).'),
            OpenApiParameter('cliente', int, description='Filtrar pelo ID do cliente.'),
            OpenApiParameter('responsavel', int, description='Filtrar pelo ID do responsável.'),
            OpenApiParameter('status', str, description='Filtrar por status.', enum=StatusMiniOS),
            OpenApiParameter('faturada', str, description='Filtrar por status de faturamento.', enum=['true', 'false']),
        ],
    ),
    create=extend_schema(
        summary='Criar Mini OS',
        description=(
            'Cria uma nova Mini OS. Se `revisao_cliente=true`, `gera_cobranca` é definido '
            'automaticamente como `true` e, ao finalizar, `data_liberacao_cobranca` e '
            '`liberada_cobranca_por` são preenchidos automaticamente.'
        ),
    ),
    retrieve=extend_schema(
        summary='Detalhar Mini OS',
        description='Retorna todos os campos de uma Mini OS pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar Mini OS',
        description=(
            'Substitui integralmente os dados de uma Mini OS. '
            'Campos calculados (`gera_cobranca`, `data_liberacao_cobranca`, '
            '`liberada_cobranca_por`, `faturada_por`) são somente leitura.'
        ),
    ),
    partial_update=extend_schema(
        summary='Atualizar Mini OS parcialmente',
        description=(
            'Atualiza um ou mais campos de uma Mini OS. '
            'Campos calculados são somente leitura e ignorados no body.'
        ),
    ),
    destroy=extend_schema(
        summary='Remover Mini OS',
        description='Remove permanentemente uma Mini OS.',
    ),
)
class MiniOSViewSet(viewsets.ModelViewSet):
    queryset = MiniOS.objects.select_related(
        'cliente',
        'servico',
        'responsavel',
        'liberada_cobranca_por',
        'faturada_por',
    ).all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MiniOSListSerializer
        return MiniOSSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.tipo_usuario == TipoUsuario.TECNICO:
            queryset = queryset.filter(responsavel=user)

        q = self.request.query_params.get('q', '').strip()
        cliente_id = self.request.query_params.get('cliente', '').strip()
        responsavel_id = self.request.query_params.get('responsavel', '').strip()
        status_param = self.request.query_params.get('status', '').strip()
        faturada = self.request.query_params.get('faturada', '').strip()

        if q:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=q) | Q(servico__nome__icontains=q)
            )
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if responsavel_id:
            queryset = queryset.filter(responsavel_id=responsavel_id)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if faturada in ('true', 'false'):
            queryset = queryset.filter(faturada=(faturada == 'true'))

        return queryset

    @extend_schema(
        summary='Faturar Mini OS',
        description=(
            'Marca a Mini OS como faturada, registrando o número da NF e o usuário responsável. '
            'Retorna 400 se a Mini OS não gerar cobrança ou ainda não estiver liberada para cobrança.'
        ),
        request=FaturarMiniOSRequestSerializer,
        responses={
            200: MiniOSSerializer,
            400: None,
        },
    )
    @action(detail=True, methods=['patch'], url_path='faturar')
    def faturar(self, request, pk=None):
        mini_os = self.get_object()
        if not mini_os.gera_cobranca:
            return Response(
                {'detail': 'Mini OS não gera cobrança.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if mini_os.data_liberacao_cobranca is None:
            return Response(
                {'detail': 'Mini OS ainda não está liberada para cobrança.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        numero_nf = request.data.get('numero_nf')
        mini_os.faturada = True
        mini_os.numero_nf = numero_nf
        mini_os.faturada_por = request.user
        mini_os.save(update_fields=['faturada', 'numero_nf', 'faturada_por', 'atualizado_em'])
        return Response(MiniOSSerializer(mini_os, context={'request': request}).data)
