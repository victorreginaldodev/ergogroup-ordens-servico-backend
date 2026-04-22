from django.db import models
from django.conf import settings


class StatusMiniOS(models.TextChoices):
    NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    FINALIZADA = 'finalizada', 'Finalizada'


class MiniOS(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='mini_os',
    )
    servico = models.ForeignKey(
        'tarefas.RepositorioMiniOS',
        on_delete=models.PROTECT,
        related_name='mini_os',
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mini_os',
    )
    quantidade = models.PositiveIntegerField(default=1)
    descricao = models.TextField(null=True, blank=True)
    data_recebimento = models.DateField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_termino = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=StatusMiniOS.choices, default=StatusMiniOS.NAO_INICIADO)
    revisao_cliente = models.BooleanField(default=False)
    faturada = models.BooleanField(default=False)
    numero_nf = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        ordering = ['-data_recebimento']
        verbose_name = 'Mini OS'
        verbose_name_plural = 'Mini OS'

    def __str__(self):
        return f'Mini OS #{self.pk} — {self.servico} ({self.cliente})'
