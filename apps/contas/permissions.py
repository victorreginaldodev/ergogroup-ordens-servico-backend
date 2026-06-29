from rest_framework.permissions import BasePermission
from apps.contas.models.choices import TipoUsuario

TIPOS_GESTORES = {
    TipoUsuario.DIRETOR,
    TipoUsuario.GESTOR_ADMINISTRATIVO,
    TipoUsuario.GESTOR_COMERCIAL,
    TipoUsuario.GESTOR_TECNICO,
    TipoUsuario.GESTOR_FINANCEIRO,
}


class IsGestor(BasePermission):
    """Diretores e gestores têm acesso completo."""
    message = 'Apenas gestores ou diretores podem realizar esta ação.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_superuser or request.user.tipo_usuario in TIPOS_GESTORES)
        )


class IsSelfOrGestor(BasePermission):
    """O próprio usuário ou um gestor pode agir sobre este objeto."""
    message = 'Sem permissão para realizar esta ação.'

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or
            obj == request.user or
            request.user.tipo_usuario in TIPOS_GESTORES
        )


TIPOS_SEM_ACESSO_A_VALORES = {
    TipoUsuario.SUB_GESTOR_TECNICO,
    TipoUsuario.TECNICO,
    TipoUsuario.GESTOR_ADMINISTRATIVO,
    TipoUsuario.ADMINISTRATIVO,
}


def usuario_pode_ver_valores(user) -> bool:
    """Indica se o usuário pode visualizar valores monetários em indicadores/BI."""
    return user.is_superuser or user.tipo_usuario not in TIPOS_SEM_ACESSO_A_VALORES


ROLES_PODEM_MODIFICAR_QUALQUER_TAREFA = {
    TipoUsuario.DIRETOR,
    TipoUsuario.GESTOR_TECNICO,
    TipoUsuario.SUB_GESTOR_TECNICO,
}


class PodeModificarTarefa(BasePermission):
    """Apenas o responsável pode modificar a tarefa. Exceções: Diretor, Líder Técnico e Sub-Líder Técnico."""

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        if request.user.is_superuser:
            return True
        if request.user.tipo_usuario in ROLES_PODEM_MODIFICAR_QUALQUER_TAREFA:
            return True
        if obj.responsavel != request.user:
            self.message = 'Apenas o responsável pela tarefa pode modificá-la.'
            return False
        return True


class PodeVerValoresFinanceiros(BasePermission):
    """Bloqueia perfis sem acesso a valores monetários nos indicadores."""
    message = 'Seu perfil não tem acesso a valores financeiros.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and usuario_pode_ver_valores(request.user)
