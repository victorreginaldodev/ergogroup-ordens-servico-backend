from django.db import models
from django.utils import timezone


class StatusServico(models.TextChoices):
    EM_ESPERA = 'em_espera', 'Em Espera'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'


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
    status = models.CharField(max_length=15, choices=StatusServico.choices, default=StatusServico.EM_ESPERA)
    data_conclusao = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['ordem_servico', 'status']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return f'Serviço #{self.pk} — OS #{self.ordem_servico_id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sincronizar_status()

    def sincronizar_status(self):
        tem_tarefas = self.tarefas.exists()
        updates = {}

        if tem_tarefas:
            todos_concluidos = not self.tarefas.exclude(status='concluida').exists()
            if todos_concluidos:
                if self.status != StatusServico.CONCLUIDA:
                    updates['status'] = StatusServico.CONCLUIDA
                if self.data_conclusao is None:
                    updates['data_conclusao'] = timezone.now().date()
            else:
                if self.status == StatusServico.CONCLUIDA:
                    updates['status'] = StatusServico.EM_ANDAMENTO
                if self.data_conclusao is not None:
                    updates['data_conclusao'] = None
        else:
            if self.status == StatusServico.CONCLUIDA:
                updates['status'] = StatusServico.EM_ANDAMENTO
            if self.data_conclusao is not None:
                updates['data_conclusao'] = None

        if updates:
            Servico.objects.filter(pk=self.pk).update(**updates)
            for campo, valor in updates.items():
                setattr(self, campo, valor)

        self.ordem_servico.atualizar_status_conclusao()
