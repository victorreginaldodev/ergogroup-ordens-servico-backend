from django.db import models
from django.conf import settings
from django.utils import timezone


class StatusTarefa(models.TextChoices):
    ABERTA = 'aberta', 'Aberta'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'
    CANCELADA = 'cancelada', 'Cancelada'


class Tarefa(models.Model):
    servico = models.ForeignKey(
        'ordens_servico.Servico',
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
    status = models.CharField(max_length=15, choices=StatusTarefa.choices, default=StatusTarefa.ABERTA)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['servico', 'status']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return f'Tarefa #{self.pk} — {self.responsavel}'

    def save(self, *args, **kwargs):
        from apps.ordens_servico.models import Servico

        hoje = timezone.localdate()
        if self.status in (StatusTarefa.EM_ANDAMENTO, StatusTarefa.CONCLUIDA) and self.data_inicio is None:
            self.data_inicio = hoje
        if self.status == StatusTarefa.CONCLUIDA and self.data_termino is None:
            self.data_termino = hoje
        if self.status != StatusTarefa.CONCLUIDA and self.data_termino is not None:
            self.data_termino = None

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
                servico_anterior.sincronizar_status_e_rastreio()

        self.servico.sincronizar_status_e_rastreio()

    def delete(self, *args, **kwargs):
        servico = self.servico
        super().delete(*args, **kwargs)
        servico.sincronizar_status_e_rastreio()
