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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sincronizar_status()

    def sincronizar_status(self):
        """Garante que o status do serviço reflita o estado das tarefas relacionadas."""
        tem_tarefas = self.tarefas.exists()
        
        campos_para_atualizar = {}

        if tem_tarefas:
            todos_concluidos = not self.tarefas.exclude(status='concluida').exists()

            if todos_concluidos:
                if self.status != 'concluida':
                    campos_para_atualizar['status'] = 'concluida'
                if self.data_conclusao is None:
                    campos_para_atualizar['data_conclusao'] = timezone.now().date()
            else:
                if self.status == 'concluida':
                    campos_para_atualizar['status'] = 'em_andamento'
                if self.data_conclusao is not None:
                    campos_para_atualizar['data_conclusao'] = None
        
        else:
            # Sem tarefas: 
            # - Permite 'em_andamento' manual.
            # - Bloqueia 'concluida' manual (reverte para 'em_andamento').
            if self.status == 'concluida':
                campos_para_atualizar['status'] = 'em_andamento'
                if self.data_conclusao is not None:
                    campos_para_atualizar['data_conclusao'] = None
            elif self.status == 'em_andamento':
                 if self.data_conclusao is not None:
                     campos_para_atualizar['data_conclusao'] = None

        if campos_para_atualizar:
            Servico.objects.filter(pk=self.pk).update(**campos_para_atualizar)
            for campo, valor in campos_para_atualizar.items():
                setattr(self, campo, valor)

        if self.ordem_servico_id:
            self.ordem_servico.atualizar_status_conclusao()

        if tem_tarefas:
            return not self.tarefas.exclude(status='concluida').exists()
        return self.status == 'concluida'

    def concluir_servico(self):
        """Mantido por compatibilidade; utiliza o fluxo de sincronização completo."""
        return self.sincronizar_status()
