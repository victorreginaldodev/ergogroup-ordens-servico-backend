from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time

class FormaPagamento(models.TextChoices):
    PIX = 'pix', 'PIX'
    CREDITO = 'credito', 'Crédito'
    DEBITO = 'debito', 'Débito'
    BOLETO = 'boleto', 'Boleto'
    TRANSFERENCIA = 'transferencia', 'Transferência'
    DINHEIRO = 'dinheiro', 'Dinheiro'
    CHEQUE = 'cheque', 'Cheque'
    OUTRO = 'outro', 'Outro'

class Prioridade(models.TextChoices):
    BAIXA = 'baixa', 'Baixa'
    MEDIA = 'media', 'Média'
    ALTA = 'alta', 'Alta'

class Status(models.TextChoices):
    ABERTA = 'aberta', 'Aberta'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'
    CANCELADA = 'cancelada', 'Cancelada'

class OrdemServico(models.Model):
    cliente = models.ForeignKey('clientes.Cliente',on_delete=models.PROTECT, related_name='ordens_servico')
    data_criacao = models.DateField()
    concluida = models.BooleanField(default=False)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ABERTA)
    prioridade = models.CharField(max_length=10, choices=Prioridade.choices, default=Prioridade.BAIXA)
    
    # Dados da cobrança
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=15, choices=FormaPagamento.choices, default=FormaPagamento.BOLETO)
    quantidade_parcelas = models.IntegerField(null=True, blank=True)
    cobranca_imediata = models.BooleanField(default=False)
    nome_contato_envio_nf = models.CharField(max_length=50, default='')
    contato_envio_nf = models.EmailField(default='')
    observacao = models.TextField(null=True, blank=True)

    # Dados do contrato
    contrato = models.BooleanField(default=False)
    objeto_contrato = models.CharField(max_length=255, null=True, blank=True)
    contrato_data_inicio = models.DateField(null=True, blank=True)
    contrato_data_fim = models.DateField(null=True, blank=True)
    gestor_contrato_nome = models.CharField(max_length=255, null=True, blank=True)
    gestor_contrato_email = models.EmailField(null=True, blank=True)
    gestor_contrato_telefone = models.CharField(max_length=30, null=True, blank=True)
    
    liberada_para_faturamento = models.BooleanField(default=False)
    liberada_para_faturamento_em = models.DateTimeField(null=True, blank=True)
    liberada_para_faturamento_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_liberadas_para_faturamento',
    )
    faturada = models.BooleanField(default=False)
    numero_nf = models.IntegerField(null=True, blank=True)
    data_faturamento = models.DateField(null=True, blank=True)
    faturada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_faturadas',
    )
    
    # Aditoria
    criada_em = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_criadas',
    )
    data_atualizacao = models.DateTimeField(auto_now=True)
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordens_atualizadas',
    )
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'

    def clean(self):
        super().clean()
        if not self.contrato:
            return

        erros = {}
        if not self.objeto_contrato:
            erros['objeto_contrato'] = 'Informe o objeto do contrato.'
        if not self.contrato_data_inicio:
            erros['contrato_data_inicio'] = 'Informe a data de início do contrato.'
        if not self.contrato_data_fim:
            erros['contrato_data_fim'] = 'Informe a data de fim do contrato.'
        if self.contrato_data_inicio and self.contrato_data_fim and self.contrato_data_fim < self.contrato_data_inicio:
            erros['contrato_data_fim'] = 'A data de fim não pode ser anterior à data de início.'
        if erros:
            raise ValidationError(erros)

    def save(self, *args, **kwargs):
        if self.pk is None and self.cobranca_imediata:
            self.liberada_para_faturamento = True
            if self.liberada_para_faturamento_em is None:
                self.liberada_para_faturamento_em = timezone.now()
            if self.liberada_para_faturamento_por_id is None:
                self.liberada_para_faturamento_por = self.criado_por
        super().save(*args, **kwargs)

    def atualizar_status_conclusao(self):
        return self.sincronizar_status_e_faturamento()

    def calcular_liberada_para_faturamento(self):
        return self.liberada_para_faturamento

    def sincronizar_status_e_faturamento(self):
        servicos = self.servicos.all()
        tem_servicos = servicos.exists()
        updates = {}

        if self.status != Status.CANCELADA:
            todos_concluidos = tem_servicos and not servicos.exclude(status='concluida').exists()
            tem_execucao = servicos.filter(status__in=['em_andamento', 'concluida']).exists()

            if todos_concluidos:
                novo_status = Status.CONCLUIDA
            elif tem_execucao:
                novo_status = Status.EM_ANDAMENTO
            else:
                novo_status = Status.ABERTA

            nova_conclusao = novo_status == Status.CONCLUIDA

            if self.status != novo_status:
                updates['status'] = novo_status
            if self.concluida != nova_conclusao:
                updates['concluida'] = nova_conclusao

        if not self.liberada_para_faturamento:
            if self.cobranca_imediata:
                updates['liberada_para_faturamento'] = True
                updates['liberada_para_faturamento_em'] = timezone.now()
                updates['liberada_para_faturamento_por_id'] = self.criado_por_id
            elif updates.get('status', self.status) == Status.CONCLUIDA:
                ultimo_servico = (
                    servicos
                    .filter(status='concluida')
                    .order_by('-data_termino', '-data_conclusao', '-id')
                    .first()
                )
                if ultimo_servico:
                    data_liberacao = ultimo_servico.data_termino or ultimo_servico.data_conclusao
                    updates['liberada_para_faturamento'] = True
                    updates['liberada_para_faturamento_em'] = (
                        _as_datetime(data_liberacao) if data_liberacao else timezone.now()
                    )
                    updates['liberada_para_faturamento_por_id'] = ultimo_servico.terminado_por_id

        if updates:
            updates['data_atualizacao'] = timezone.now()
            OrdemServico.objects.filter(pk=self.pk).update(**updates)
            for campo, valor in updates.items():
                setattr(self, campo, valor)

        return self.concluida

    def __str__(self):
        return f'OS #{self.pk} — {self.cliente}'


def _as_datetime(value):
    dt = datetime.combine(value, time.min)
    return timezone.make_aware(dt, timezone.get_current_timezone())
