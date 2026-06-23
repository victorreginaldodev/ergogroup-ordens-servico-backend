from django.db import models
from django.conf import settings
from django.utils import timezone


class StatusServico(models.TextChoices):
    ABERTO = 'aberto', 'Aberto'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluído'
    CANCELADO = 'cancelado', 'Cancelado'


class Servico(models.Model):
    ordem_servico = models.ForeignKey(
        'ordem_servico.OrdemServico',
        on_delete=models.CASCADE,
        related_name='servicos',
    )
    repositorio = models.ForeignKey(
        'servicos.Repositorio',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    descricao = models.TextField()
    status = models.CharField(max_length=15, choices=StatusServico.choices, default=StatusServico.ABERTO)
    data_inicio = models.DateField(null=True, blank=True)
    data_termino = models.DateField(null=True, blank=True)
    data_conclusao = models.DateField(null=True, blank=True)
    terminado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servicos_terminados',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ordem_servico', 'status']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return f'Serviço #{self.pk} — OS #{self.ordem_servico_id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sincronizar_status_e_rastreio()

    def sincronizar_status(self):
        return self.sincronizar_status_e_rastreio()

    def sincronizar_status_e_rastreio(self):
        tem_tarefas = self.tarefas.exists()
        updates = {}

        if self.status == StatusServico.CANCELADO:
            self.ordem_servico.sincronizar_status_e_faturamento()
            return self.status

        if tem_tarefas:
            tarefas = self.tarefas.all()
            primeira_data_inicio = (
                tarefas
                .filter(data_inicio__isnull=False)
                .order_by('data_inicio', 'id')
                .values_list('data_inicio', flat=True)
                .first()
            )
            ultima_tarefa_concluida = (
                tarefas
                .filter(status='concluida')
                .order_by('-data_termino', '-atualizado_em', '-id')
                .first()
            )
            todos_concluidos = not tarefas.exclude(status='concluida').exists()
            tem_execucao = tarefas.filter(status__in=['em_andamento', 'concluida']).exists()

            if self.data_inicio != primeira_data_inicio:
                updates['data_inicio'] = primeira_data_inicio

            if todos_concluidos:
                if self.status != StatusServico.CONCLUIDA:
                    updates['status'] = StatusServico.CONCLUIDA
                data_termino = (
                    ultima_tarefa_concluida.data_termino
                    if ultima_tarefa_concluida and ultima_tarefa_concluida.data_termino
                    else timezone.localdate()
                )
                terminado_por_id = (
                    ultima_tarefa_concluida.responsavel_id
                    if ultima_tarefa_concluida
                    else None
                )
                if self.data_termino != data_termino:
                    updates['data_termino'] = data_termino
                if self.data_conclusao != data_termino:
                    updates['data_conclusao'] = data_termino
                if self.terminado_por_id != terminado_por_id:
                    updates['terminado_por_id'] = terminado_por_id
            else:
                novo_status = StatusServico.EM_ANDAMENTO if tem_execucao else StatusServico.ABERTO
                if self.status != novo_status:
                    updates['status'] = novo_status
                if self.data_termino is not None:
                    updates['data_termino'] = None
                if self.data_conclusao is not None:
                    updates['data_conclusao'] = None
                if self.terminado_por_id is not None:
                    updates['terminado_por_id'] = None
        else:
            if self.status != StatusServico.ABERTO:
                updates['status'] = StatusServico.ABERTO
            if self.data_inicio is not None:
                updates['data_inicio'] = None
            if self.data_termino is not None:
                updates['data_termino'] = None
            if self.data_conclusao is not None:
                updates['data_conclusao'] = None
            if self.terminado_por_id is not None:
                updates['terminado_por_id'] = None

        if updates:
            updates['atualizado_em'] = timezone.now()
            Servico.objects.filter(pk=self.pk).update(**updates)
            for campo, valor in updates.items():
                setattr(self, campo, valor)

        self.ordem_servico.sincronizar_status_e_faturamento()
        return self.status
