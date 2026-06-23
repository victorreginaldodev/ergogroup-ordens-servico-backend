from django.db import models
from django.conf import settings
from django.utils import timezone


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
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    revisao_cliente = models.BooleanField(default=False)
    gera_cobranca = models.BooleanField(default=False)
    data_liberacao_cobranca = models.DateTimeField(null=True, blank=True)
    liberada_cobranca_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mini_os_liberadas_cobranca',
    )
    faturada = models.BooleanField(default=False)
    numero_nf = models.CharField(max_length=10, null=True, blank=True)
    faturada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mini_os_faturadas',
    )

    class Meta:
        ordering = ['-data_recebimento']
        verbose_name = 'Mini OS'
        verbose_name_plural = 'Mini OS'

    def __str__(self):
        return f'Mini OS #{self.pk} — {self.servico} ({self.cliente})'

    def clean(self):
        super().clean()
        self.gera_cobranca = self.revisao_cliente

    def save(self, *args, **kwargs):
        hoje = timezone.localdate()
        if self.status in (StatusMiniOS.EM_ANDAMENTO, StatusMiniOS.FINALIZADA) and self.data_inicio is None:
            self.data_inicio = hoje
        if self.status == StatusMiniOS.FINALIZADA and self.data_termino is None:
            self.data_termino = hoje
        if self.status != StatusMiniOS.FINALIZADA and self.data_termino is not None:
            self.data_termino = None
        self.gera_cobranca = self.revisao_cliente
        if self.gera_cobranca and self.status == StatusMiniOS.FINALIZADA:
            if self.data_liberacao_cobranca is None:
                self.data_liberacao_cobranca = timezone.now()
            if self.liberada_cobranca_por_id is None:
                self.liberada_cobranca_por = self.responsavel
        if not self.gera_cobranca:
            self.data_liberacao_cobranca = None
            self.liberada_cobranca_por = None
        super().save(*args, **kwargs)
