from django.db import models
from django.utils import timezone

from .Repositorio import Repositorio
from .OrdemServico import OrdemServico

class Servico(models.Model):

    STATUS = (
        ('em_espera', 'EM ESPERA'),
        ('em_andamento', 'EM ANDAMENTO'),
        ('concluida', 'CONCLUÍDA'),
    )
    ordem_servico = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, null=True, blank=True, related_name='servicos')
    repositorio = models.ForeignKey(Repositorio, on_delete=models.CASCADE, null=True, blank=True)
    descricao = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=15, null=True, blank=True, choices=STATUS, default='em_espera')
    data_conclusao = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'Ordem de serviço: {self.ordem_servico.id} | Cliente: {self.ordem_servico.cliente.nome}'


    def concluir_servico(self):
        # Verifica se todas as tarefas associadas estão concluídas
        if all(tarefa.status == 'concluida' for tarefa in self.tarefas.all()):
            # Atualiza o status do serviço para 'concluída' e define a data de conclusão
            self.status = 'concluida'
            self.data_conclusao = timezone.now().date()
            self.save()
