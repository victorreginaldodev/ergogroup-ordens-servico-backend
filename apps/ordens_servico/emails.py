import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.contas.models import Usuario
from apps.contas.models.choices import TipoUsuario
from apps.contas.permissions import usuario_pode_ver_valores
from apps.ordens_servico.models.ordem_servico import Prioridade

logger = logging.getLogger(__name__)

CORES_PRIORIDADE = {
    Prioridade.BAIXA: '#64748B',
    Prioridade.MEDIA: '#EAB308',
    Prioridade.ALTA: '#EF4444',
}


def _usuarios_ativos(*tipos):
    queryset = Usuario.objects.filter(is_active=True, ativo=True).exclude(email='')
    if tipos:
        queryset = queryset.filter(tipo_usuario__in=tipos)
    return queryset


def _enviar(assunto, template, contexto, destinatarios):
    if not settings.EMAIL_NOTIFICATIONS_ENABLED:
        return 0

    destinatarios = list(dict.fromkeys(destinatarios))
    if not destinatarios:
        return 0

    html_content = render_to_string(template, contexto)
    email = EmailMultiAlternatives(
        assunto,
        assunto,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios,
    )
    email.attach_alternative(html_content, 'text/html')
    # Notificação por e-mail nunca pode derrubar a operação de negócio que a
    # disparou: isso roda dentro de transaction.on_commit, no mesmo request,
    # e uma falha de SMTP aqui já quebrou a aplicação inteira no passado.
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception('Falha ao enviar e-mail de notificação: %s', assunto)
        return 0
    return len(destinatarios)


def notificar_criacao_contrato(ordem_servico):
    usuarios = list(_usuarios_ativos())
    if not usuarios:
        return 0

    com_valores = [u.email for u in usuarios if usuario_pode_ver_valores(u)]
    sem_valores = [u.email for u in usuarios if not usuario_pode_ver_valores(u)]

    assunto = f'Novo contrato criado - OS #{ordem_servico.pk}'
    total = 0
    total += _enviar(
        assunto,
        'emails/novo_contrato_os.html',
        {'ordem_servico': ordem_servico, 'mostrar_valores': True},
        com_valores,
    )
    total += _enviar(
        assunto,
        'emails/novo_contrato_os.html',
        {'ordem_servico': ordem_servico, 'mostrar_valores': False},
        sem_valores,
    )
    return total


def notificar_atribuicao_tarefa(tarefa):
    responsavel = tarefa.responsavel
    if not responsavel or not responsavel.email:
        return 0

    assunto = f'Nova tarefa atribuída a você - Tarefa #{tarefa.pk}'
    contexto = {
        'tarefa': tarefa,
        'prioridade_cor': CORES_PRIORIDADE.get(tarefa.prioridade, '#64748B'),
    }
    return _enviar(assunto, 'emails/tarefa_atribuida.html', contexto, [responsavel.email])


def notificar_liberacao_cobranca(instancia, tipo, valor=None):
    destinatarios = [
        u.email for u in _usuarios_ativos(TipoUsuario.GESTOR_FINANCEIRO, TipoUsuario.FINANCEIRO)
    ]
    if not destinatarios:
        return 0

    assunto = f'{tipo} #{instancia.pk} liberada para cobrança'
    contexto = {
        'tipo': tipo,
        'numero': instancia.pk,
        'cliente': instancia.cliente,
        'valor': valor,
        'liberada_em': getattr(instancia, 'liberada_para_cobranca_em', None) or getattr(instancia, 'data_liberacao_cobranca', None),
        'liberada_por': _nome_usuario(
            getattr(instancia, 'liberada_para_cobranca_por', None) or getattr(instancia, 'liberada_cobranca_por', None)
        ),
    }
    return _enviar(assunto, 'emails/liberacao_cobranca.html', contexto, destinatarios)


def notificar_cobranca_realizada(instancia, tipo, valor=None):
    destinatarios = [
        u.email for u in _usuarios_ativos(
            TipoUsuario.GESTOR_FINANCEIRO,
            TipoUsuario.FINANCEIRO,
            TipoUsuario.GESTOR_COMERCIAL,
            TipoUsuario.COMERCIAL,
        )
    ]
    if not destinatarios:
        return 0

    assunto = f'{tipo} #{instancia.pk} - cobrança realizada'
    contexto = {
        'tipo': tipo,
        'numero': instancia.pk,
        'cliente': instancia.cliente,
        'valor': valor,
        'numero_nf': instancia.numero_nf,
        'data_cobranca': getattr(instancia, 'data_cobranca', None),
        'realizada_por': _nome_usuario(instancia.cobranca_realizada_por),
    }
    return _enviar(assunto, 'emails/cobranca_realizada.html', contexto, destinatarios)


def _nome_usuario(usuario):
    if not usuario:
        return None
    return usuario.nome_completo or usuario.email
