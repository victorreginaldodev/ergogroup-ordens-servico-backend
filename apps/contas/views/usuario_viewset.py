from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from apps.contas.models.choices import TipoUsuario
from apps.contas.serializers import (
    UsuarioListSerializer,
    UsuarioDetailSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    AlterarSenhaSerializer,
    TipoOpcaoSerializer,
    DetalheSerializer,
)
from apps.contas.permissions import IsGestor, IsSelfOrGestor

Usuario = get_user_model()


@extend_schema_view(
    list=extend_schema(
        summary='Listar usuários',
        description=(
            'Retorna a lista paginada de usuários com campos resumidos. '
            'Suporta busca textual e filtragem por tipo e status.'
        ),
        parameters=[
            OpenApiParameter(
                'q', str,
                description='Busca por nome completo ou e-mail (parcial, sem distinção de maiúsculas).',
            ),
            OpenApiParameter(
                'tipo', str,
                description='Filtrar por tipo de usuário.',
                enum=TipoUsuario,
            ),
            OpenApiParameter(
                'ativo', str,
                description='Filtrar por status de ativação.',
                enum=['true', 'false'],
            ),
        ],
    ),
    create=extend_schema(
        summary='Criar usuário',
        description='Cria um novo usuário. Requer perfil Gestor ou superior.',
    ),
    retrieve=extend_schema(
        summary='Detalhar usuário',
        description='Retorna todos os campos cadastrais de um usuário pelo seu ID.',
    ),
    update=extend_schema(
        summary='Atualizar usuário',
        description=(
            'Substitui integralmente os dados cadastrais de um usuário. '
            'Cada usuário pode editar o próprio cadastro; gestores podem editar qualquer usuário.'
        ),
    ),
    partial_update=extend_schema(
        summary='Atualizar usuário parcialmente',
        description=(
            'Atualiza um ou mais campos cadastrais de um usuário. '
            'Cada usuário pode editar o próprio cadastro; gestores podem editar qualquer usuário.'
        ),
    ),
    destroy=extend_schema(
        summary='Remover usuário',
        description='Remove permanentemente um usuário. Requer perfil Gestor ou superior.',
    ),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by('nome_completo')

    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        if self.action == 'create':
            return UsuarioCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UsuarioUpdateSerializer
        return UsuarioDetailSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'ativar', 'desativar'):
            return [IsAuthenticated(), IsGestor()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), IsSelfOrGestor()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        tipo = self.request.query_params.get('tipo', '').strip()
        ativo = self.request.query_params.get('ativo', '').strip()

        if q:
            queryset = queryset.filter(
                Q(nome_completo__icontains=q) | Q(email__icontains=q)
            )
        if tipo:
            queryset = queryset.filter(tipo_usuario=tipo)
        if ativo in ('true', 'false'):
            queryset = queryset.filter(ativo=(ativo == 'true'))

        return queryset

    @extend_schema(
        summary='Dados do usuário autenticado',
        description='Retorna os dados completos do usuário identificado pelo token JWT.',
        responses={200: UsuarioDetailSerializer},
    )
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = UsuarioDetailSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary='Alterar senha',
        description=(
            'Altera a senha de um usuário. Cada usuário pode alterar a própria senha '
            'informando a senha atual. Diretores e Gestores Administrativos podem '
            'alterar a senha de qualquer usuário sem informar a senha atual.'
        ),
        request=AlterarSenhaSerializer,
        responses={
            200: DetalheSerializer,
            400: None,
            403: None,
        },
    )
    @action(detail=True, methods=['patch'], url_path='alterar-senha')
    def alterar_senha(self, request, pk=None):
        usuario = self.get_object()
        if usuario != request.user and not (request.user.is_superuser or request.user.tipo_usuario in {TipoUsuario.DIRETOR, TipoUsuario.GESTOR_ADMINISTRATIVO}):
            return Response(
                {'detail': 'Sem permissão para alterar a senha deste usuário.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AlterarSenhaSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        usuario.set_password(serializer.validated_data['nova_senha'])
        usuario.save(update_fields=['password'])
        return Response({'detail': 'Senha alterada com sucesso.'})

    @extend_schema(
        summary='Ativar usuário',
        description='Marca um usuário como ativo, permitindo que ele acesse o sistema. Requer perfil Gestor ou superior.',
        request=None,
        responses={200: DetalheSerializer},
    )
    @action(detail=True, methods=['patch'], url_path='ativar')
    def ativar(self, request, pk=None):
        usuario = self.get_object()
        usuario.ativo = True
        usuario.save(update_fields=['ativo'])
        return Response({'detail': f'Usuário {usuario.nome_completo} ativado com sucesso.'})

    @extend_schema(
        summary='Desativar usuário',
        description=(
            'Marca um usuário como inativo, bloqueando o acesso ao sistema. '
            'Requer perfil Gestor ou superior. Não é possível desativar o próprio usuário.'
        ),
        request=None,
        responses={
            200: DetalheSerializer,
            400: None,
        },
    )
    @action(detail=True, methods=['patch'], url_path='desativar')
    def desativar(self, request, pk=None):
        usuario = self.get_object()
        if usuario == request.user:
            return Response(
                {'detail': 'Não é possível desativar o próprio usuário.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usuario.ativo = False
        usuario.save(update_fields=['ativo'])
        return Response({'detail': f'Usuário {usuario.nome_completo} desativado com sucesso.'})

    @extend_schema(
        summary='Listar tipos de usuário',
        description='Retorna todos os tipos de usuário disponíveis no sistema com seus rótulos.',
        responses={200: TipoOpcaoSerializer(many=True)},
    )
    @action(detail=False, methods=['get'], url_path='tipos')
    def tipos(self, request):
        return Response([{'value': v, 'label': l} for v, l in TipoUsuario.choices])
