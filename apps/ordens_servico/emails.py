from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from apps.contas.models import Usuario


def notificar_criacao_contrato(ordem_servico):
    destinatarios = list(
        Usuario.objects
        .filter(is_active=True, ativo=True)
        .exclude(email='')
        .values_list('email', flat=True)
        .distinct()
    )
    if not destinatarios:
        return 0

    assunto = f'Novo contrato criado - OS #{ordem_servico.pk}'
    contexto = {'ordem_servico': ordem_servico}
    html_content = render_to_string('emails/novo_contrato_os.html', contexto)
    text_content = (
        f'Novo contrato criado na OS #{ordem_servico.pk} para '
        f'{ordem_servico.cliente.nome}.\n'
        f'Objeto: {ordem_servico.objeto_contrato}\n'
        f'Vigência: {ordem_servico.contrato_data_inicio} a {ordem_servico.contrato_data_fim}'
    )

    email = EmailMultiAlternatives(
        assunto,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        destinatarios,
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=False)
    return len(destinatarios)
