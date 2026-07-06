from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.ordens_servico.emails import notificar_criacao_contrato
from apps.ordens_servico.models import OrdemServico


@receiver(post_save, sender=OrdemServico)
def enviar_email_novo_contrato(sender, instance, created, **kwargs):
    if not created or not instance.contrato:
        return

    transaction.on_commit(lambda: notificar_criacao_contrato(instance))
