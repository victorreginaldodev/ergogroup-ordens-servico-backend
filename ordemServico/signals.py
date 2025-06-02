from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from ordemServico.models import OrdemServico, Servico, Tarefa, Cliente, Profile

# ENVIA E-MAIL DE CLIENTE CRIADO
@receiver(post_save, sender=Cliente)
def send_new_cliente_notification(sender, instance, created, **kwargs):
    if created:        
        perfis_notificacao = Profile.objects.filter(role__in=[1, 2, 3])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]

        subject = f'Novo Cliente Criado: {instance.nome}'
        
        context = {
            'cliente': instance
        }
        
        # Renderizando o conteúdo HTML do template
        html_content = render_to_string('emails/novo_cliente.html', context)
        
        # Criando a versão em texto simples
        text_content = strip_tags(html_content)  # Remove as tags HTML para gerar uma versão de texto simples

        # Enviando o e-mail usando EmailMultiAlternatives
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")  # Anexa a versão HTML
        try:
            msg.send()
            print("E-mail HTML enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail HTML: {e}")

# ENVIA E-MAIL DE ORDEM DE SERVIÇO CRIADA
@receiver(post_save, sender=OrdemServico)
def send_new_ordem_servico_notification(sender, instance, created, **kwargs):
    if created:
        # Perfis que devem receber a notificação
        perfis_notificacao = Profile.objects.filter(role__in=[1, 2])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]

        subject = f'Nova Ordem de Serviço Criada para o Cliente: {instance.cliente.nome}'
        
        # Contexto contendo os dados da ordem de serviço e seus serviços relacionados
        context = {
            'ordem_servico': instance,
        }
        
        # Renderizando o conteúdo HTML do template
        html_content = render_to_string('emails/nova_ordem_servico.html', context)
        
        # Criando a versão em texto simples
        text_content = strip_tags(html_content)

        # Enviando o e-mail usando EmailMultiAlternatives
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print("E-mail HTML enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail HTML: {e}")

# ENVIA E-MAL DE SERVIÇO CRIADO
@receiver(post_save, sender=Servico)
def send_new_servico_notification(sender, instance, created, **kwargs):
    if created:
        perfis_notificacao = Profile.objects.filter(role__in=[1, 3])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]
        
        subject = f'Nova Ordem de Serviço Criada para o Cliente: {instance.ordem_servico.cliente.nome}'
        
        context = {
            'servico': instance, 
        }
        
        html_content = render_to_string('emails/novo_servico.html', context)
        
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print("E-mail HTML enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail HTML: {e}")

# ENVIA E-MAIL DE SERVIÇO FINALIZADO
@receiver(pre_save, sender=Servico)
def send_servico_completed_notification(sender, instance, **kwargs):
    # Pegamos a instância anterior no banco de dados para verificar o status atual
    try:
        servico_anterior = Servico.objects.get(pk=instance.pk)
    except Servico.DoesNotExist:
        servico_anterior = None

    # Verifica se o status mudou para 'concluída'
    if servico_anterior and servico_anterior.status != 'concluida' and instance.status == 'concluida':
        perfis_notificacao = Profile.objects.filter(role__in=[1, 3])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]

        subject = f'Serviço Concluído para o Cliente: {instance.ordem_servico.cliente.nome}'

        context = {
            'servico': instance,
        }

        html_content = render_to_string('emails/servico_concluido.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print("E-mail de conclusão enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail de conclusão: {e}")

# ENVIA E-MAIL DE NOVA TAREFA
@receiver(post_save, sender=Tarefa)
def send_new_task_notification(sender, instance, created, **kwargs):
    if created:
        # Pega o e-mail do profile relacionado à tarefa
        destinatario = instance.profile.user.email

        subject = f'Nova Tarefa Criada: {instance.servico.repositorio.nome}'
        
        # Cria o contexto para o template do e-mail
        context = {
            'tarefa': instance,
            'profile': instance.profile,
            'servico': instance.servico,
            'ordem_servico': instance.ordem_servico,
        }
        
        # Renderiza o conteúdo HTML do template de e-mail
        html_content = render_to_string('emails/nova_tarefa.html', context)
        text_content = strip_tags(html_content)  # Cria a versão em texto simples removendo as tags HTML

        # Configura o e-mail
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [destinatario])
        msg.attach_alternative(html_content, "text/html")  # Anexa a versão HTML do e-mail

        try:
            # Tenta enviar o e-mail
            msg.send()
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

# ENVIA E-MAIL DE SERVIÇO FINALIZADO
@receiver(pre_save, sender=Tarefa)
def send_task_completed_notification(sender, instance, **kwargs):
    # Pegamos a instância anterior no banco de dados para verificar o status atual
    try:
        tarefa_anterior = Tarefa.objects.get(pk=instance.pk)
    except Tarefa.DoesNotExist:
        tarefa_anterior = None

    # Verifica se o status mudou para 'concluída'
    if tarefa_anterior and tarefa_anterior.status != 'concluida' and instance.status == 'concluida':
        perfis_notificacao = Profile.objects.filter(role__in=[1, 3])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]

        subject = 'Uma tarefa foi concluída!'

        context = {
            'tarefa': instance,
        }

        html_content = render_to_string('emails/tarefa_concluida.html', context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print("E-mail de conclusão enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail de conclusão: {e}")

# ENVIA E-EMAIL ORDEM DE SERVIÇO FATURADA
@receiver(pre_save, sender=OrdemServico)
def send_faturamento_notification(sender, instance, **kwargs):
    # Pegamos a instância anterior no banco de dados para verificar o faturamento atual
    try:
        ordem_anterior = OrdemServico.objects.get(pk=instance.pk)
    except OrdemServico.DoesNotExist:
        ordem_anterior = None

    # Verifica se o faturamento mudou para 'sim'
    if ordem_anterior and ordem_anterior.faturamento != 'sim' and instance.faturamento == 'sim':
        # Perfis com roles 1 e 2 que receberão a notificação
        perfis_notificacao = Profile.objects.filter(role__in=[1, 2])
        destinatarios = [perfil.user.email for perfil in perfis_notificacao]

        subject = f'Faturamento Realizado: {instance.cliente.nome}'

        # Contexto para o template do e-mail
        context = {
            'ordem_servico': instance,
            'cliente': instance.cliente,
            'valor': instance.valor,
            'data_faturamento': instance.data_faturamento,
            'forma_pagamento': instance.get_forma_pagamento_display(),
            'servicos': Servico.objects.filter(ordem_servico=instance)
        }

        # Renderiza o conteúdo HTML do template de e-mail
        html_content = render_to_string('emails/faturamento_realizado.html', context)
        text_content = strip_tags(html_content)  # Remove as tags HTML para criar a versão de texto simples

        # Configura o e-mail
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, destinatarios)
        msg.attach_alternative(html_content, "text/html")  # Anexa a versão HTML do e-mail

        try:
            # Envia o e-mail
            msg.send()
            print("E-mail de faturamento enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail de faturamento: {e}")
