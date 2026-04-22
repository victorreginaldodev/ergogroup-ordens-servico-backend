from django.db import models
from django.conf import settings


class FormaPagamento(models.TextChoices):
    PIX = 'pix', 'PIX'
    CREDITO = 'credito', 'Crédito'
    DEBITO = 'debito', 'Débito'
    BOLETO = 'boleto', 'Boleto'
    TRANSFERENCIA = 'transferencia', 'Transferência'
    DINHEIRO = 'dinheiro', 'Dinheiro'
    CHEQUE = 'cheque', 'Cheque'
    OUTRO = 'outro', 'Outro'


QUANTIDADE_PARCELAS = [(i, f'{i} parcela{"s" if i > 1 else ""}') for i in range(1, 13)]


class OrdemServico(models.Model):
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='ordens_servico',
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_criadas',
    )

    data_criacao = models.DateField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=15, choices=FormaPagamento.choices, default=FormaPagamento.BOLETO)
    quantidade_parcelas = models.IntegerField(choices=QUANTIDADE_PARCELAS, null=True, blank=True)
    cobranca_imediata = models.BooleanField(default=False)

    nome_contato_envio_nf = models.CharField(max_length=50, default='')
    contato_envio_nf = models.EmailField(default='')
    observacao = models.TextField(null=True, blank=True)

    concluida = models.BooleanField(default=False)
    faturada = models.BooleanField(default=False)
    numero_nf = models.IntegerField(null=True, blank=True)
    data_faturamento = models.DateField(null=True, blank=True)

    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'

    def liberada_para_faturamento(self):
        if self.cobranca_imediata:
            return True
        servicos = self.servicos.all()
        return servicos.exists() and not servicos.exclude(status='concluida').exists()

    def atualizar_status_conclusao(self):
        servicos = self.servicos.all()
        concluida = servicos.exists() and not servicos.exclude(status='concluida').exists()
        if self.concluida != concluida:
            self.concluida = concluida
            self.save(update_fields=['concluida'])
        return self.concluida

    def __str__(self):
        return f'OS #{self.pk} — {self.cliente}'
