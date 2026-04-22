from django.db import models
from django.conf import settings


class StatusTarefa(models.TextChoices):
    NAO_INICIADA = 'nao_iniciada', 'Não Iniciada'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'


class Tarefa(models.Model):
    servico = models.ForeignKey(
        'servicos.Servico',
        on_delete=models.CASCADE,
        related_name='tarefas',
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tarefas',
    )
    descricao = models.TextField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_termino = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=StatusTarefa.choices, default=StatusTarefa.NAO_INICIADA)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['servico', 'status']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return f'Tarefa #{self.pk} — {self.responsavel}'

    def save(self, *args, **kwargs):
        from apps.servicos.models import Servico

        servico_anterior_id = None
        if self.pk:
            servico_anterior_id = (
                Tarefa.objects.filter(pk=self.pk)
                .values_list('servico_id', flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        if servico_anterior_id and servico_anterior_id != self.servico_id:
            servico_anterior = Servico.objects.filter(pk=servico_anterior_id).first()
            if servico_anterior:
                servico_anterior.sincronizar_status()

        self.servico.sincronizar_status()

    def delete(self, *args, **kwargs):
        servico = self.servico
        super().delete(*args, **kwargs)
        servico.sincronizar_status()
