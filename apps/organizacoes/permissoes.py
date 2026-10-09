"""Catálogo de permissões do sistema e verificação de acesso.

As regras da API perguntam por códigos de permissão (``tem_permissao``), nunca por tipo
de usuário. Nesta fase as permissões de cada usuário vêm do ``tipo_usuario`` pela tabela
``PERMISSOES_POR_TIPO_USUARIO``; depois passarão a vir das funções que ele exerce nos
setores, sem mudar quem pergunta. Ver docs/mapa-de-permissoes.md.
"""
from django.db import models
from rest_framework.permissions import BasePermission

from apps.contas.models.choices import TipoUsuario


class Permissao(models.TextChoices):
    OS_VER_TODAS = 'os.ver_todas', 'Ver todas as OS, serviços e tarefas'
    OS_GERENCIAR = 'os.gerenciar', 'Criar e editar OS e seus serviços'
    OS_EXCLUIR = 'os.excluir', 'Excluir OS'
    OS_OPERACIONAL_GERENCIAR = 'os_operacional.gerenciar', 'Criar e editar OS operacionais e o catálogo operacional'
    FINANCEIRO_VER_VALORES = 'financeiro.ver_valores', 'Ver valores e condições de pagamento'
    FINANCEIRO_REGISTRAR_COBRANCA = 'financeiro.registrar_cobranca', 'Registrar cobrança e nota fiscal'
    CLIENTES_GERENCIAR = 'clientes.gerenciar', 'Criar, editar e excluir clientes'
    CATALOGO_GERENCIAR = 'catalogo.gerenciar', 'Criar, editar e excluir o catálogo de serviços'
    SERVICOS_VER_SETOR = 'servicos.ver_setor', 'Ver os serviços e tarefas do setor'
    SERVICOS_GERENCIAR = 'servicos.gerenciar', 'Ajustar e excluir serviços do setor'
    TAREFAS_DISTRIBUIR = 'tarefas.distribuir', 'Criar, reatribuir e excluir tarefas'
    TAREFAS_EDITAR_SETOR = 'tarefas.editar_setor', 'Editar qualquer tarefa do setor'
    USUARIOS_GERENCIAR = 'usuarios.gerenciar', 'Criar, editar, ativar e desativar usuários'
    USUARIOS_GERENCIAR_DIRETORIA = 'usuarios.gerenciar_diretoria', 'Gerenciar usuários da diretoria'
    USUARIOS_REDEFINIR_SENHA = 'usuarios.redefinir_senha', 'Alterar a senha de outros usuários'
    ORGANIZACAO_CONFIGURAR = 'organizacao.configurar', 'Configurar organização e setores'
    INDICADORES_VER_GERAL = 'indicadores.ver_geral', 'Ver indicadores de toda a equipe'
    AUDITORIA_VER = 'auditoria.ver', 'Ver o histórico de auditoria'


# Permissões que valem só nos setores do vínculo que as concede; as demais valem para a organização toda.
PERMISSOES_POR_SETOR = frozenset({
    Permissao.SERVICOS_VER_SETOR, Permissao.SERVICOS_GERENCIAR,
    Permissao.TAREFAS_DISTRIBUIR, Permissao.TAREFAS_EDITAR_SETOR,
})


def escopo_da_permissao(permissao) -> str:
    return 'setor' if permissao in PERMISSOES_POR_SETOR else 'global'


# Perfis que o frontend trata como diretoria (o gestor comercial tem o mesmo acesso do diretor).
TIPOS_DIRETORIA = frozenset({TipoUsuario.DIRETOR, TipoUsuario.GESTOR_COMERCIAL})

_P = Permissao
_TODAS = frozenset(Permissao)
_BASE_ESCRITORIO = frozenset({
    _P.OS_VER_TODAS, _P.OS_GERENCIAR, _P.CLIENTES_GERENCIAR,
    _P.INDICADORES_VER_GERAL, _P.AUDITORIA_VER,
})
_GESTAO_DE_PESSOAS = frozenset({_P.USUARIOS_GERENCIAR, _P.ORGANIZACAO_CONFIGURAR})
_EXECUCAO = frozenset({
    _P.SERVICOS_VER_SETOR, _P.SERVICOS_GERENCIAR, _P.TAREFAS_DISTRIBUIR, _P.TAREFAS_EDITAR_SETOR,
})

# Reproduz as travas do frontend (docs/mapa-de-permissoes.md, seção 5) com as decisões de 09/10/2026.
PERMISSOES_POR_TIPO_USUARIO = {
    TipoUsuario.DIRETOR: _TODAS,
    TipoUsuario.GESTOR_COMERCIAL: _TODAS,
    TipoUsuario.COMERCIAL: _BASE_ESCRITORIO | {
        _P.FINANCEIRO_VER_VALORES, _P.CATALOGO_GERENCIAR, _P.OS_OPERACIONAL_GERENCIAR,
    },
    TipoUsuario.GESTOR_TECNICO: _BASE_ESCRITORIO | _EXECUCAO | _GESTAO_DE_PESSOAS | {
        _P.FINANCEIRO_VER_VALORES, _P.CATALOGO_GERENCIAR, _P.OS_OPERACIONAL_GERENCIAR,
    },
    TipoUsuario.SUB_GESTOR_TECNICO: _EXECUCAO | {
        _P.OS_VER_TODAS, _P.CLIENTES_GERENCIAR, _P.CATALOGO_GERENCIAR, _P.OS_OPERACIONAL_GERENCIAR,
        _P.INDICADORES_VER_GERAL, _P.AUDITORIA_VER,
    },
    TipoUsuario.TECNICO: frozenset({
        _P.CLIENTES_GERENCIAR, _P.OS_OPERACIONAL_GERENCIAR, _P.AUDITORIA_VER,
    }),
    TipoUsuario.GESTOR_FINANCEIRO: _BASE_ESCRITORIO | _GESTAO_DE_PESSOAS | {
        _P.FINANCEIRO_VER_VALORES, _P.FINANCEIRO_REGISTRAR_COBRANCA, _P.OS_OPERACIONAL_GERENCIAR,
    },
    TipoUsuario.FINANCEIRO: _BASE_ESCRITORIO | {
        _P.FINANCEIRO_VER_VALORES, _P.FINANCEIRO_REGISTRAR_COBRANCA, _P.OS_OPERACIONAL_GERENCIAR,
    },
    TipoUsuario.GESTOR_ADMINISTRATIVO: _BASE_ESCRITORIO | _GESTAO_DE_PESSOAS | {
        _P.USUARIOS_REDEFINIR_SENHA, _P.OS_OPERACIONAL_GERENCIAR,
    },
    TipoUsuario.ADMINISTRATIVO: _BASE_ESCRITORIO,
}


def permissoes_do_usuario(usuario) -> frozenset:
    if usuario is None or not usuario.is_authenticated or not usuario.is_active:
        return frozenset()
    if usuario.is_superuser:
        return _TODAS
    cache = getattr(usuario, '_permissoes_cache', None)
    if cache is None:
        cache = PERMISSOES_POR_TIPO_USUARIO.get(usuario.tipo_usuario, frozenset())
        usuario._permissoes_cache = cache
    return cache


def tem_permissao(usuario, permissao, setor=None) -> bool:
    """Indica se o usuário tem a permissão. ``setor`` passa a valer quando as permissões vierem dos setores."""
    return permissao in permissoes_do_usuario(usuario)


class TemPermissao(BasePermission):
    """Exige ao menos uma das permissões informadas. Uso: ``TemPermissao(Permissao.X, Permissao.Y)``."""
    message = 'Seu perfil não tem permissão para esta ação.'

    def __init__(self, *permissoes):
        self.permissoes = permissoes

    def has_permission(self, request, view):
        return any(tem_permissao(request.user, p) for p in self.permissoes)


class PermissoesPorAcaoMixin:
    """Para viewsets: ``permissoes_por_acao = {'create': (Permissao.X,), ...}``. Ações fora do mapa
    exigem só autenticação; ações no mapa exigem ao menos uma das permissões listadas."""
    permissoes_por_acao = {}

    def get_permissions(self):
        permissoes = super().get_permissions()
        exigidas = self.permissoes_por_acao.get(self.action)
        if exigidas:
            permissoes.append(TemPermissao(*exigidas))
        return permissoes
